import unittest

from macro_methods import *


TEST_STRING = r"""
                \documentclass[11pt,reqno]{amsart}                
                \newcommand{\F}{\mathcal{F}} % trasformata di Fourier
                \renewcommand{\L}{\mathcal{L}} % trasformata di Laplace
                \newcommand{\LL}{\L^2} % trasformata di Laplace                
                \newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}
                \begin{document}
                    \noindent
                    Student's surname and name \underline{\hspace{68.5ex}}
                    \vspace{1.5ex} % tst comment 
                    \noindent
                    Student's number \underline{\hspace{80ex}}                    
                    \vspace{8ex}
                    This formula is weird:
                    $$\lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$
                    
                    \noindent
                \end{document}
            """
STRING_NO_COMMENTS = r"""
                \documentclass[11pt,reqno]{amsart}                
                \newcommand{\F}{\mathcal{F}} 
                \renewcommand{\L}{\mathcal{L}} 
                \newcommand{\LL}{\L^2}                
                \newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}
                \begin{document}
                    \noindent 
                    Student's surname and name \underline{\hspace{68.5ex}}
                    \vspace{1.5ex} 
                    \noindent
                    Student's number \underline{\hspace{80ex}}                    
                    \vspace{8ex}
                    This formula is weird:
                    $$\lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$
                    
                    \noindent
                \end{document}
            """


class AxessCleanerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_strip_comments(self):
        self.assertNotEqual(STRING_NO_COMMENTS,TEST_STRING)
        self.assertEqual(STRING_NO_COMMENTS.replace(" ", ""), strip_comments(TEST_STRING).replace(" ", ""))

    def test_parse_macro_structure(self):
        text = r"\newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}"
        dict_ok = {
                    'command_type': 'newcommand',
                    'macro_name': '\\weird',
                    'separator_open': '{',
                    'separator_close': '}',
                    'number_of_inputs': '3',
                    'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}'
               }

        dict_not = {
                    'command_type': 'newcommand',
                    'macro_name': '\\werd',
                    'separator_open': '#',
                    'separator_close': '}',
                    'number_of_inputs': '3',
                    'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2'
               }

        self.assertEqual(parse_macro_structure(text), dict_ok)
        self.assertNotEqual(parse_macro_structure(text), dict_not)

    def test_gather_macro(self):
        array_test = [
                {
                    'command_type': 'newcommand',
                    'macro_name': '\\F',
                    'separator_open': '{', 'separator_close': '}',
                    'number_of_inputs': None,
                    'raw_replacement': '\\mathcal{F}'
                },
                {
                    'command_type': 'renewcommand',
                    'macro_name': '\\L',
                    'separator_open': '{',
                    'separator_close': '}',
                    'number_of_inputs': None,
                    'raw_replacement': '\\mathcal{L}'
                },
                {
                    'command_type': 'newcommand',
                    'macro_name': '\\LL',
                    'separator_open': '{',
                    'separator_close': '}',
                    'number_of_inputs': None,
                    'raw_replacement': '\\L^2'
                },
                {
                    'command_type': 'newcommand',
                    'macro_name': '\\weird',
                    'separator_open': '{',
                    'separator_close': '}',
                    'number_of_inputs': '3',
                    'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}'
                }
        ]
        array_from_function = gather_macro(TEST_STRING)

        self.assertEqual(array_from_function[1], array_test[1])
        self.assertEqual(array_from_function[3], array_test[3])
        self.assertNotEqual(array_from_function[1], array_test[2])

    def test_get_expanded_macros(self):

        dict_ok = {
            'command_type': 'newcommand',
            'macro_name': '\\weird',
            'separator_open': '{',
            'separator_close': '}',
            'number_of_inputs': '3',
            'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}'
        }

        dict_not = {
            'command_type': 'newcommand',
            'macro_name': '\\werd',
            'separator_open': '#',
            'separator_close': '}',
            'number_of_inputs': '3',
            'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2'
        }

        self.assertEqual(get_expanded_macro([dict_ok]), [enrich_regexp(dict_ok)])
        self.assertNotEqual(get_expanded_macro([dict_ok]), [enrich_regexp(dict_not)])


    def test_remove_macro(self):
        string_new = remove_macro(TEST_STRING, None, gather_macro(TEST_STRING))

        string_to_be = r"""\documentclass[11pt,reqno]{amsart}                
                \newcommand{\F}{\mathcal{F}} % trasformata di Fourier
                \renewcommand{\L}{\mathcal{L}} % trasformata di Laplace
                \newcommand{\LL}{\L^2} % trasformata di Laplace                
                \newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}
                \begin{document}
                    \noindent
                    Student's surname and name \underline{\hspace{68.5ex}}
                    \vspace{1.5ex} % tst comment 
                    \noindent
                    Student's number \underline{\hspace{80ex}}                    
                    \vspace{8ex}
                    This formula is weird:
                    $$\lim_{x\to\alpha} \gamma=\log_a_r \sum_{n\ =\ \frac{1}{\{\mathcal{L}^2\}}}^{a}\ \mathcal{F}(\alpha)\ -\ 7\ +\frac{\frac{1}{\{\mathcal{L}^2\}}}{a}\ d$$
                    \noindent
                \end{document}
                """
        self.assertEqual(string_new.strip(), string_to_be.strip())


    def test_enrich_regexp(self):

        dict_ok = {
            'command_type': 'newcommand',
            'macro_name': '\\weird',
            'separator_open': '{',
            'separator_close': '}',
            'number_of_inputs': '3',
            'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}'
        }

        enriched_dict_ok = {
            'sub': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
            'reg': '\\\\weird',
            'macro': {'command_type': 'newcommand',
                      'macro_name': '\\weird',
                      'separator_open': '{',
                      'separator_close': '}',
                      'number_of_inputs': '3',
                      'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}'
                      },
            'multi': True}

        self.assertEqual(dict_ok, enrich_regexp(dict_ok)["macro"])
        self.assertEqual(enriched_dict_ok, enrich_regexp(dict_ok))

    def test_recursive_expansion(self):
        available_macros = get_expanded_macro(gather_macro(TEST_STRING))

        line =  recursive_expansion(r"$$\lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$",
                                    available_macros
                                    )
        line_to_be = (r"$$\lim_{x\to\alpha} \gamma=\log_a_r \sum_{n\ =\ \frac{1}{\{\mathcal{L}^2\}}}^{a}\ "  
                       r"\mathcal{F}(\alpha)\ -\ 7\ +\frac{\frac{1}{\{\mathcal{L}^2\}}}{a}\ d$$")
        self.assertEqual(line_to_be, line)

    def test_multi_substitution_regexp(self):

        macro = {
            'sub': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
            'reg': '\\\\weird',
            'macro': {'command_type': 'newcommand',
                      'macro_name': '\\weird',
                      'separator_open': '{',
                      'separator_close': '}',
                      'number_of_inputs': '3',
                      'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}'
                      },
            'multi': True}

        string_to_test = multi_substitution_regexp( macro,
                                                    r"{\frac{1}{\{\LL\}}}{a}\alpha d$$")
        string_to_match = r"\sum_{n = \frac{1}{\{\LL\}}}^{a} \F(\alpha) - 7 +\frac{\frac{1}{\{\LL\}}}{a} d$$"

        self.assertEqual(string_to_test, string_to_match)



if __name__ == '__main__':
    unittest.main()
