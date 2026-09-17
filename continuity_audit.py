"""Read-only, metadata-level dependency checks. Changed bytes require review, not new claims.
No page is written and no review date/baseline is advanced by a scan.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
import json, os, re
from pathlib import Path, PurePosixPath
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import quote
from urllib.error import HTTPError, URLError

SHA = re.compile(r'[0-9a-f]{40}')
REPO = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')


def instant(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None: raise ValueError('timezone required')
    return dt.astimezone(timezone.utc)


def validate_manifest(data):
    if data.get('schema') != 'eternities.claim-dependencies/v1': raise ValueError('schema')
    seen = set()
    if not isinstance(data.get('claims'), list) or not 1 <= len(data['claims']) <= 100:
        raise ValueError('bounded claim list')
    for c in data['claims']:
        if not isinstance(c.get('id'), str) or not re.fullmatch(r'[a-z0-9-]{1,100}', c['id']) or c['id'] in seen:
            raise ValueError('unique claim ID')
        seen.add(c['id']); instant(c['reviewed_at'])
        if type(c.get('max_review_age_days')) is not int or not 1 <= c['max_review_age_days'] <= 366:
            raise ValueError('bounded review age')
        if not isinstance(c.get('surfaces'), list) or not c['surfaces']:
            raise ValueError('affected surfaces required')
        if c.get('approval') not in ('reviewed', 'pending', 'revoked'):
            raise ValueError('approval state')
        deps = c.get('sources')
        if not isinstance(deps, list) or not 1 <= len(deps) <= 20: raise ValueError('bounded dependencies')
        for s in deps:
            if not REPO.fullmatch(s['repo']) or not SHA.fullmatch(s['reviewed_blob']):
                raise ValueError('repository and Git blob required')
            path = PurePosixPath(s['path'])
            if path.is_absolute() or any(x in ('..', '.') for x in path.parts) or '\\' in s['path'] or not s['path']:
                raise ValueError('relative source path')
            if not re.fullmatch(r'[A-Za-z0-9_./-]{1,200}', s['ref']): raise ValueError('bounded ref')
    return data


def key(source): return source['repo'] + ':' + source['ref'] + ':' + source['path']


def evaluate(manifest, observations, now):
    validate_manifest(manifest)
    if now.tzinfo is None: raise ValueError('aware clock required')
    items = []
    for claim in manifest['claims']:
        reasons, details = [], []
        if claim['approval'] != 'reviewed': reasons.append('approval-' + claim['approval'])
        reviewed = instant(claim['reviewed_at'])
        if reviewed > now: reasons.append('review-time-in-future')
        elif now - reviewed > timedelta(days=claim['max_review_age_days']): reasons.append('review-overdue')
        for src in claim['sources']:
            ob = observations.get(key(src), {})
            status = ob.get('status', 'unavailable')
            if status == 'observed':
                if not SHA.fullmatch(str(ob.get('blob', ''))) or not SHA.fullmatch(str(ob.get('commit', ''))):
                    state = 'unavailable'
                else:
                    try: age = now - instant(ob['observed_at'])
                    except (KeyError, ValueError): age = timedelta(days=999)
                    if age.total_seconds() < 0 or age > timedelta(hours=24): state = 'observation-expired'
                    else: state = 'unchanged-at-observation' if ob['blob'] == src['reviewed_blob'] else 'source-changed'
            elif status == 'missing': state = 'source-missing-or-inaccessible'
            else: state = 'unavailable'
            details.append({'source': key(src), 'state': state, 'observed_commit': ob.get('commit')})
            if state != 'unchanged-at-observation': reasons.append(state)
        items.append({'id': claim['id'], 'state': 'review-needed' if reasons else 'no-drift-detected',
                      'reasons': sorted(set(reasons)), 'surfaces': claim['surfaces'], 'sources': details,
                      'reviewed_at': claim['reviewed_at']})
    return {'schema': 'eternities.continuity-audit/v1', 'checked_at': now.isoformat(), 'claims': items,
            'review_required': any(c['reasons'] for c in items), 'automatic_publication': False,
            'limits': 'Only listed source files and supplied review decisions; unchanged bytes do not prove truth, release, deployment, or complete coverage.'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('GitHub API redirects are not followed with credentials')


def github_json(path, token):
    if not path.startswith('/repos/') or '..' in path: raise ValueError('bounded GitHub endpoint')
    req = Request('https://api.github.com' + path,
                  headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                           'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Eternities-Continuity-Review/0.1'})
    with build_opener(NoRedirect()).open(req, timeout=15) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000: raise ValueError('response bound')
        return json.loads(raw)


def observe(manifest, token, now):
    validate_manifest(manifest); out, commits, trees = {}, {}, {}
    for claim in manifest['claims']:
        for src in claim['sources']:
            k = key(src)
            if k in out: continue
            if not token:
                out[k] = {'status': 'unavailable', 'reason': 'No read credential configured'}; continue
            try:
                repo, ref = src['repo'], src['ref']
                pair = (repo, ref)
                if pair not in commits:
                    result = github_json('/repos/' + repo + '/commits/' + quote(ref, safe=''), token)
                    commits[pair] = (result['sha'], result['commit']['tree']['sha'])
                commit, tree = commits[pair]
                if not SHA.fullmatch(commit) or not SHA.fullmatch(tree): raise ValueError('commit binding')
                parts = PurePosixPath(src['path']).parts
                file = None
                for index, part in enumerate(parts):
                    tk = (repo, tree)
                    if tk not in trees:
                        entries = github_json('/repos/' + repo + '/git/trees/' + tree, token)
                        if entries.get('truncated'): raise ValueError('incomplete tree')
                        trees[tk] = entries['tree']
                    file = next((entry for entry in trees[tk] if entry['path'] == part), None)
                    if file is None: raise ValueError('missing source path')
                    if index < len(parts) - 1:
                        if file.get('type') != 'tree' or file.get('mode') != '040000': raise ValueError('directory expected')
                        tree = file['sha']
                if file.get('type') != 'blob' or file.get('mode') not in ('100644', '100755') or not SHA.fullmatch(file.get('sha', '')):
                    raise ValueError('regular file expected, symlinks and submodules refused')
                out[k] = {'status': 'observed', 'blob': file['sha'], 'commit': commit, 'observed_at': now.isoformat()}
            except HTTPError as exc:
                out[k] = {'status': 'missing' if exc.code == 404 else 'unavailable', 'reason': 'HTTP ' + str(exc.code)}
            except (URLError, ValueError, KeyError, TypeError, TimeoutError):
                out[k] = {'status': 'unavailable', 'reason': 'Bounded read failed; no freshness assertion'}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='company/claims.json')
    parser.add_argument('--observations', help='Previously captured metadata for deterministic local review')
    parser.add_argument('--output', default='artifacts/continuity/report.json')
    parser.add_argument('--at', help='Explicit ISO timestamp, for local fixtures only')
    args = parser.parse_args()
    now = instant(args.at) if args.at else datetime.now(timezone.utc)
    manifest = validate_manifest(json.loads(Path(args.manifest).read_text(encoding='utf-8')))
    observations = json.loads(Path(args.observations).read_text(encoding='utf-8')) if args.observations else observe(manifest, os.environ.get('CONTINUITY_READ_TOKEN') or os.environ.get('GITHUB_TOKEN'), now)
    report = evaluate(manifest, observations, now)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    lines = ['# Publication source review', '', 'Scan time: ' + now.isoformat(), '',
             'Source changes are review signals, not automatically changed public claims.', '']
    for c in report['claims']:
        lines += ['## ' + c['id'], c['state'], 'Affected surfaces: ' + ', '.join(c['surfaces']),
                  'Reasons: ' + (', '.join(c['reasons']) or 'No listed drift detected'), '']
    output.with_suffix('.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Review required' if report['review_required'] else 'No listed drift detected')
    return 2 if report['review_required'] else 0

if __name__ == '__main__': raise SystemExit(main())
