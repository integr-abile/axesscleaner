import unittest

from axesscleaner import parse_macro_structure

from hashlib import md5

class axesscleanerTest(unittest.TestCase):
    def test_parse_macro_structure(self):
        text = r"\newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}"
        dict = {
                    'command_type': 'newcommand',
                    'macro_name': '\\weird',
                    'separator_open': '{', 'separator_close': '}',
                    'number_of_inputs': '3',
                    'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}'
               }

        self.assertEqual(parse_macro_structure(text), dict)


if __name__ == '__main__':
    unittest.main()
