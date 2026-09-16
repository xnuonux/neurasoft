import unittest

from public_search import extract_main_text


class PublicSearchTests(unittest.TestCase):
    def test_indexes_nested_main_content_not_site_chrome(self):
        source = '<header>boilerplate</header><main><h1>Memory</h1><section><h2>Self-model</h2><p>A consequence can change learning.</p></section></main><footer>footer</footer>'
        self.assertEqual(extract_main_text(source), 'Memory Self-model A consequence can change learning.')

    def test_excludes_code_styles_and_hidden_content(self):
        source = '<main><p>Visible &amp; useful.</p><script>secret-code</script><style>.rule {}</style><div hidden><p>hidden details</p></div><svg aria-hidden="true"><text>decoration</text></svg><p>End.</p></main>'
        self.assertEqual(extract_main_text(source), 'Visible & useful. End.')

    def test_no_main_is_not_an_accidental_full_document_index(self):
        self.assertEqual(extract_main_text('<p>private metadata</p>'), '')
