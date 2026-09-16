"""Authored explanatory SVGs. Illustrations, not plots or resident telemetry."""
from itertools import count

_ids = count(1)


def continuum(kind='hero'):
    uid = f'continuum-{next(_ids)}'
    return f'''<figure class="continuum-art motion-piece" data-continuum>
<svg viewBox="0 0 600 490" role="img" aria-labelledby="{uid}-title {uid}-desc">
<title id="{uid}-title">A history that leaves the future open</title><desc id="{uid}-desc">Recorded encounters remain distinct. Their relevance meets at a present choice, with several possible continuations. This is a conceptual illustration, not a trace of Luna.</desc>
<defs><linearGradient id="{uid}-green" x1="0" x2="1"><stop stop-color="#b9c9ad"/><stop offset=".58" stop-color="#55715a"/><stop offset="1" stop-color="#94aa85"/></linearGradient></defs>
<path class="ribbon-wash" d="M28 200 C155 190 188 365 311 266 C378 211 435 62 580 122 L580 153 C437 98 388 242 314 292 C183 380 137 237 28 231 Z" fill="url(#{uid}-green)"/>
<path class="ribbon-wash secondary" d="M28 342 C158 346 206 207 310 260 C421 317 465 395 580 361 L580 375 C462 414 413 337 308 282 C204 226 161 362 28 359 Z" fill="#baac90"/>
<g class="continuity-lines" fill="none" stroke="#6c8569" stroke-width="1.1">
<path d="M28 215 C156 201 186 378 312 277 C388 216 434 77 580 137"/>
<path d="M28 230 C147 218 204 367 312 277 C410 197 451 200 580 215"/>
<path d="M28 344 C154 360 203 207 312 277 C421 346 469 402 580 370"/>
<path d="M28 355 C159 365 213 230 312 277 C422 329 482 291 580 297"/>
</g><path class="flow-trace" d="M28 215 C156 201 186 378 312 277 C388 216 434 77 580 137" fill="none" stroke="#365d47" stroke-width="2" stroke-dasharray="3 240"/>
<g fill="#f3f1e9" stroke="#365d47" stroke-width="1.4"><circle cx="63" cy="220" r="5"/><circle cx="139" cy="260" r="5"/><circle cx="211" cy="305" r="5"/><circle cx="312" cy="277" r="9"/></g>
<path d="M63 208V153 M312 263V190 M552 139V99" stroke="#98a48e" fill="none"/>
<g class="art-label" fill="#365d47"><text x="28" y="123">01 / RETAIN</text><text x="277" y="160">02 / RECONSIDER</text><text x="438" y="70">03 / CONTINUE</text></g>
<g class="art-word" fill="#243c32"><text x="28" y="143">An encounter.</text><text x="277" y="181">A present choice.</text><text x="438" y="91">An open future.</text></g>
<path d="M28 431H580" stroke="#cbd2c2"/><text class="art-footnote" x="28" y="456">The record remains. What it means can change.</text>
</svg><figcaption>Continuity, illustrated. Not a resident measurement.</figcaption></figure>'''


def study(kind=0):
    uid = f'study-{next(_ids)}'
    if kind % 3 == 1:
        # One history, two possible decisions. Every line has an explanatory role.
        drawing = '''<path d="M70 162H256 C336 162 334 100 409 100H555 M256 162C336 162 334 226 409 226H555"/><g class="diagram-paper"><rect x="67" y="130" width="72" height="64" rx="5"/><rect x="156" y="130" width="72" height="64" rx="5"/></g><circle cx="278" cy="162" r="7"/><path class="diagram-dashed" d="M409 100H555"/><text x="68" y="107">SAVED ENCOUNTERS</text><text x="409" y="81">RECONSIDER</text><text x="409" y="258">CONTINUE</text><path d="M83 149H122M83 160H113M83 174H119M172 149H210M172 160H202M172 174H207"/>'''
    elif kind % 3 == 2:
        drawing = '''<path d="M66 153H170 M210 153C298 153 299 94 354 94H561 M210 153C298 153 299 236 354 236H561"/><circle cx="189" cy="153" r="20"/><path d="M366 87V101M431 87V101M496 87V101M561 87V101 M366 229V243M431 229V243M496 229V243M561 229V243"/><text x="63" y="119">SHARED START</text><text x="355" y="66">CANDIDATE MECHANISM</text><text x="355" y="208">MATCHED ALTERNATIVE</text><path class="diagram-dashed" d="M366 109V221M431 109V221M496 109V221M561 109V221"/>'''
    else:
        drawing = '''<path d="M70 110H565 M70 222H565"/><g class="diagram-paper"><rect x="94" y="84" width="103" height="52" rx="4"/><rect x="248" y="84" width="103" height="52" rx="4"/><rect x="403" y="84" width="103" height="52" rx="4"/></g><path d="M145 144V201 M300 144V201 M455 144V201"/><circle cx="145" cy="222" r="7"/><circle cx="300" cy="222" r="7"/><circle cx="455" cy="222" r="7"/><text x="70" y="62">WHAT HAPPENED</text><text x="70" y="274">WHAT WE MAKE OF IT</text>'''
    return f'<svg class="editorial-diagram" viewBox="0 0 640 330" role="img" aria-labelledby="{uid}"><title id="{uid}">Conceptual illustration of {("records and revisable interpretation", "history and open choices", "matched experimental comparisons")[kind % 3]}</title><g>{drawing}</g></svg>'
