/* Shared by the actual page and its dependency-free tests. */
((root) => {
  'use strict';
  const normalize = value => String(value || '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  function searchPages(pages, query, limit = 12) {
    const phrase = normalize(query);
    const words = phrase.split(/\s+/).filter(Boolean);
    if (!words.length) return pages.slice(0, limit);
    return pages.map((page, order) => {
      const title = normalize(page.title), description = normalize(page.description), body = normalize(page.text);
      const all = `${title} ${description} ${body}`;
      const score = words.every(word => all.includes(word))
        ? words.reduce((sum, word) => sum + (title.includes(word) ? 8 : 0) + (description.includes(word) ? 3 : 0) + (body.includes(word) ? 1 : 0), 0) + (all.includes(phrase) ? 5 : 0)
        : 0;
      return {page, score, order};
    }).filter(item => item.score > 0).sort((a, b) => b.score - a.score || a.order - b.order).slice(0, limit).map(item => item.page);
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {searchPages};
  else root.NeurasoftSearch = {searchPages};
})(globalThis);
