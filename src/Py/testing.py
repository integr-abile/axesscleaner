import unittest

from Axesscleaner import Macro


TEST_STRING = r"""
                \documentclass[11pt,reqno]{amsart}                
                \newcommand{\F}{\mathcal{F}} % trasformata di Fourier
                \renewcommand{\L}{\mathcal{L}} % trasformata di Laplace
                \newcommand{\LL}{\L^2} % trasformata di Laplace                
                \newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}
                \DeclareMathOperator{\im}{Im}
                \begin{document}
                    \noindent
                    Student's surname and name \underline{\hspace{68.5ex}}
                    \vspace{1.5ex} % tst comment 
                    \noindent
                    Student's number \underline{\hspace{80ex}}                    
                    \vspace{8ex}
                    This formula is weird:
                    $$\im \lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$
                    
                    \noindent
                \end{document}
            """
STRING_NO_COMMENTS = r"""
                \documentclass[11pt,reqno]{amsart}                
                \newcommand{\F}{\mathcal{F}} 
                \renewcommand{\L}{\mathcal{L}} 
                \newcommand{\LL}{\L^2}                
                \newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}
                \DeclareMathOperator{\im}{Im}
                \begin{document}
                    \noindent 
                    Student's surname and name \underline{\hspace{68.5ex}}
                    \vspace{1.5ex} 
                    \noindent
                    Student's number \underline{\hspace{80ex}}                    
                    \vspace{8ex}
                    This formula is weird:
                    $$\im \lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$
                    
                    \noindent
                \end{document}
            """


class AxessCleanerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_strip_comments(self):

        axmacro = Macro.Methods()

        self.assertNotEqual(STRING_NO_COMMENTS,TEST_STRING)
        self.assertEqual(STRING_NO_COMMENTS.replace(" ", ""), axmacro.strip_comments(TEST_STRING).replace(" ", ""))

    def test_macro_entity_init(self):

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
           'raw_replacement': '\\sumz_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2'
        }

        macro = Macro.Macro(dict_ok)

        self.assertEqual(macro.raw_replacement, dict_ok["raw_replacement"])
        self.assertEqual(macro.macro_name, dict_ok["macro_name"])
        self.assertEqual(macro.number_of_inputs, dict_ok["number_of_inputs"])
        self.assertEqual(macro.command_type, dict_ok["command_type"])
        self.assertEqual(macro.multi, True)
        self.assertNotEqual(macro.raw_replacement, dict_not["raw_replacement"])

    def test_enhance_raw_replacement(self):

        axmacro = Macro.Methods()

        axmacro.gather_macro('\DeclareMathOperator{\im}{Im}')

        self.assertEqual(axmacro.macro_list[0].raw_replacement, '\\operatorname{Im}')
        self.assertNotEqual(axmacro.macro_list[0].raw_replacement, 'Im')


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
            'command_type': 'newcommand',
            'macro_name': '\\weird',
            'separator_open': '{',
            'separator_close': '}',
            'number_of_inputs': '3',
            'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
            'multi': True,
            'escape_name': '\\\\weird',
            'regexp': '\\\\weird\\s*(.*$)'
        }

        macro = Macro.Macro(dict_ok)

        self.assertEqual(macro.regexp, enriched_dict_ok["regexp"])
        self.assertEqual(macro.escape_name, enriched_dict_ok["escape_name"])

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
            'command_type': 'newcommand',
            'macro_name': '\\weird',
            'separator_open': '{',
            'separator_close': '}',
            'number_of_inputs': '3',
            'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
            'multi': True,
            'escape_name': '\\\\weird',
            'regexp': '\\\\weird\\s*(.*$)'
        }

        macro = Macro.Macro(dict_ok)

        self.assertEqual(enriched_dict_ok, macro.to_dict())

    def test_is_not_empty(self):

        macro = Macro.Macro({})

        self.assertEqual(macro.is_not_empty(), False)

    def test_parse_macro_structure(self):

        text = r"\newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}"
        dict_ok = {
            'command_type': 'newcommand',
            'macro_name': '\\weird',
            'separator_open': '{',
            'separator_close': '}',
            'number_of_inputs': '3',
            'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
            'multi': True,
            'escape_name': '\\\\weird',
            'regexp': '\\\\weird\\s*(.*$)'
        }

        dict_not = {
            'command_type': 'newcommand',
            'macro_name': '\\weird',
            'separator_open': '{',
            'separator_close': '}',
            'number_of_inputs': '3',
            'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
            'multi': False,
            'escape_name': '\\\\weird',
            'regexp': '\\\\weird\\s*(.*$)'
        }

        axmacro = Macro.Methods()

        self.assertEqual(axmacro.parse_macro_structure(text).to_dict(), dict_ok)
        self.assertNotEqual(axmacro.parse_macro_structure(text).to_dict(), dict_not)

    def test_gather_macro(self):
        array_test = [
            {
                'command_type': 'newcommand',
                'macro_name': '\\F',
                'separator_open': '{',
                'separator_close': '}',
                'number_of_inputs': None,
                'raw_replacement': '\\mathcal{F}',
                'multi': False,
                'escape_name': '\\\\F',
                'regexp': '\\\\F(?![a-zA-Z])'
            },
            {
                'command_type': 'renewcommand',
                'macro_name': '\\L',
                'separator_open': '{',
                'separator_close': '}',
                'number_of_inputs': None,
                'raw_replacement': '\\mathcal{L}',
                'multi': False,
                'escape_name': '\\\\L',
                'regexp': '\\\\L(?![a-zA-Z])'
            },
            {
                'command_type': 'newcommand',
                'macro_name': '\\LL',
                'separator_open': '{',
                'separator_close': '}',
                'number_of_inputs': None,
                'raw_replacement': '\\L^2',
                'multi': False,
                'escape_name': '\\\\LL',
                'regexp': '\\\\LL(?![a-zA-Z])'
            },
            {
                'command_type': 'newcommand',
                'macro_name': '\\weird',
                'separator_open': '{',
                'separator_close': '}',
                'number_of_inputs': '3',
                'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
                'multi': True,
                'escape_name': '\\\\weird',
                'regexp': '\\\\weird\\s*(.*$)'
            }
        ]

        axmacro = Macro.Methods()
        print(axmacro.macro_list)
        axmacro.gather_macro(TEST_STRING)

        self.assertEqual(axmacro.macro_list[1].to_dict(), array_test[1])
        self.assertEqual(axmacro.macro_list[3].to_dict(), array_test[3])
        self.assertNotEqual(axmacro.macro_list[1].to_dict(), array_test[3])

    def test_remove_macro(self):
        axmacro = Macro.Methods()

        axmacro.gather_macro(TEST_STRING)

        string_new = axmacro.remove_macro(TEST_STRING, None)

        string_to_be = r"""\documentclass[11pt,reqno]{amsart}                
                \newcommand{\F}{\mathcal{F}} % trasformata di Fourier
                \renewcommand{\L}{\mathcal{L}} % trasformata di Laplace
                \newcommand{\LL}{\L^2} % trasformata di Laplace                
                \newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}
                \DeclareMathOperator{\im}{Im}
                \begin{document}
                    \noindent
                    Student's surname and name \underline{\hspace{68.5ex}}
                    \vspace{1.5ex} % tst comment 
                    \noindent
                    Student's number \underline{\hspace{80ex}}                    
                    \vspace{8ex}
                    This formula is weird:
                    $$\operatorname{Im} \lim_{x\to\alpha} \gamma=\log_a_r \sum_{n\ =\ \frac{1}{\{\mathcal{L}^2\}}}^{a}\ \mathcal{F}(\alpha)\ -\ 7\ +\frac{\frac{1}{\{\mathcal{L}^2\}}}{a}\ d$$
                    \noindent
                \end{document}
                """
        self.assertEqual(string_new.strip(), string_to_be.strip())

    def test_recursive_expansion(self):

        axmacro = Macro.Methods()

        axmacro.gather_macro(TEST_STRING)

        line = axmacro.recursive_expansion(r"$$\lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$")
        line_to_be = (r"$$\lim_{x\to\alpha} \gamma=\log_a_r \sum_{n\ =\ \frac{1}{\{\mathcal{L}^2\}}}^{a}\ "  
                       r"\mathcal{F}(\alpha)\ -\ 7\ +\frac{\frac{1}{\{\mathcal{L}^2\}}}{a}\ d$$")
        self.assertEqual(line_to_be, line)

    def test_multi_substitution_regexp(self):

        axmacro = Macro.Methods()

        macro = Macro.Macro({'command_type': 'newcommand',
                             'macro_name': '\\weird',
                             'separator_open': '{',
                             'separator_close': '}',
                             'number_of_inputs': '3',
                             'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
                            })

        string_to_test = axmacro.multi_substitution_regexp( macro,
                                                    r"{\frac{1}{\{\LL\}}}{a}\alpha d$$")
        string_to_match = r"\sum_{n = \frac{1}{\{\LL\}}}^{a} \F(\alpha) - 7 +\frac{\frac{1}{\{\LL\}}}{a} d$$"

        self.assertEqual(string_to_test, string_to_match)



if __name__ == '__main__':
    unittest.main()
