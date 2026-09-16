"""Build a local search corpus from the public main element, never source files."""
from html.parser import HTMLParser
import re


class _MainText(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.stack = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'main':
            self.in_main = True
        if not self.in_main:
            return
        attrs = dict(attrs)
        hidden = (self.stack[-1][1] if self.stack else False) or tag in {'script', 'style', 'svg'} or 'hidden' in attrs or attrs.get('aria-hidden') == 'true'
        if tag not in self.VOID:
            self.stack.append((tag, hidden))

    def handle_endtag(self, tag):
        if not self.in_main:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        if tag == 'main':
            self.in_main = False

    def handle_data(self, text):
        if self.in_main and not (self.stack and self.stack[-1][1]):
            self.parts.append(text)


def extract_main_text(source):
    parser = _MainText()
    parser.feed(source)
    return re.sub(r'\s+', ' ', ' '.join(parser.parts)).strip()
