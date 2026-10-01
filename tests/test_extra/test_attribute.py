"""Test attribute selectors."""
from .. import util
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        import platform

        if platform.system() == 'Windows':
            with self.assertRaises(sv.SelectorSyntaxError):
                sv.compile('[a="' + ('x' * 300))
        else:
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(3)

            passed = False
            try:
                with self.assertRaises(sv.SelectorSyntaxError):
                    sv.compile('[a="' + ('x' * 300))
                passed = True
            except TimeoutError:
                pass
            finally:
                signal.alarm(0)
            self.assertTrue(passed)

    def test_bad_attribute_unclosed_double_quote(self):
        """Test unclosed double quoted attribute values fail for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout('[a="' + ('x' * 300))
        self.assert_syntax_error_no_timeout('div [a!="' + ('x' * 300))
        self.assert_syntax_error_no_timeout('[a^="' + ('x' * 300) + ']')

    def test_bad_attribute_unclosed_single_quote(self):
        """Test unclosed single quoted attribute values fail for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout("[a='" + ('x' * 300))
        self.assert_syntax_error_no_timeout("div [a~='" + ('x' * 300))
        self.assert_syntax_error_no_timeout("[a$='" + ('x' * 300) + ']')

    def test_attribute_long_quoted_value(self):
        """Test long quoted attribute values, including escapes and escaped newlines, still match."""

        markup = """
        <div id="div">
        <p id="0" title="{}"></p>
        <p id="1" title="{}"></p>
        <p id="2" title="xyxy"></p>
        </div>
        """.format('x' * 300, "x'y" * 100)

        self.assert_selector(markup, '[title="' + ('x' * 300) + '"]', ['0'], flags=util.HTML)
        self.assert_selector(markup, "[title='" + ('x' * 300) + "']", ['0'], flags=util.HTML)
        self.assert_selector(markup, "[title='" + ("x\\'y" * 100) + "']", ['1'], flags=util.HTML)
        self.assert_selector(markup, '[title="' + ('x\\\ny' * 2) + '"]', ['2'], flags=util.HTML)
