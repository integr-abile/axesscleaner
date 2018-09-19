import unittest

from Axesscleaner import Macro, Text


TEST_STRING = (r"\documentclass[11pt,reqno]{amsart}"
               "\n"
               r"\newcommand{\F}{\mathcal{F}} % trasformata di Fourier"
               "\n"
               r"\renewcommand{\L}{\mathcal{L}} % trasformata di Laplace"
               "\n"
               r"\newcommand{\LL}{\L^2} % trasformata di Laplace"
               "\n"
               r"\newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}"
               "\n"
               r"\DeclareMathOperator{\im}{Im}"
               "\n"
               r"\begin{document}"
               "\n"
               r"$"
               "\n"
               r"\begin{tabular}{l}"
               "\n"
               r"$ \displaystyle (+\L )^{\displaystyle +\L}=+\L $"
               "\n"
               r"\\"
               "\n"
               r"$\displaystyle    (+\L)^{-\L} =0$ "
               "\n"
               r"\end{tabular}"
               "\n"
               r"$"
               "\n"                                       
               r"\noindent"
               "\n"
               r"Student's surname and name \underline{\hspace{68.5ex}}"
               "\n"
               r"\vspace{1.5ex} % tst comment"
               "\n"
               r"\noindent"
               "\n"
               r"Student's number \underline{\hspace{80ex}}"
               "\n"
               r"\vspace{8ex}"
               "\n" 
               r"This formula is weird:"
               "\n"
               r"$$\im \lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$"
               "\n"
               r"\noindent"
               "\n"
               r"\end{document}"
               )
STRING_NO_COMMENTS = (r"\documentclass[11pt,reqno]{amsart}"
               "\n"
               r"\newcommand{\F}{\mathcal{F}} "
               "\n"
               r"\renewcommand{\L}{\mathcal{L}} "
               "\n"
               r"\newcommand{\LL}{\L^2} "
               "\n"                       
               r"\newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}"
               "\n"
               r"\DeclareMathOperator{\im}{Im}"
               "\n"
               r"\begin{document}"
               "\n"
               r"$"
               "\n"
               r"\begin{tabular}{l}"
               "\n"
               r"$ \displaystyle (+\L )^{\displaystyle +\L}=+\L $"
               "\n"
               r"\\"
               "\n"
               r"$\displaystyle    (+\L)^{-\L} =0$ "
               "\n"
               r"\end{tabular}"
               "\n"
               r"$"                      
               "\n"
               r"\noindent"
               "\n"
               r"Student's surname and name \underline{\hspace{68.5ex}}"
               "\n"
               r"\vspace{1.5ex} "
               "\n"
               r"\noindent"
               "\n"
               r"Student's number \underline{\hspace{80ex}}"
               "\n"
               r"\vspace{8ex}"
               "\n" 
               r"This formula is weird:"
               "\n"
               r"$$\im \lim_{x\to\alpha} \gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$"
               "\n"
               r"\noindent"
               "\n"
               r"\end{document}"
                      )

class AxessCleanerMacro(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

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

    def test_is_not_empty(self):

        macro = Macro.Macro({})

        self.assertEqual(macro.is_not_empty(), False)


class AxessCleanerMacroMethods(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_strip_comments(self):

        axmacro = Macro.Methods()

        self.assertNotEqual(STRING_NO_COMMENTS, TEST_STRING)
        self.assertEqual(STRING_NO_COMMENTS, axmacro.strip_comments(TEST_STRING))

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
                'command_type': 'renewcommand',
                'macro_name': '\\LL',
                'separator_open': '{',
                'separator_close': '}',
                'number_of_inputs': None,
                'raw_replacement': '{\mathcal{L}}^2',
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
            },
            {
                'command_type': 'DeclareMathOperator',
                'macro_name': '\\im',
                'separator_open': '{',
                'separator_close': '}',
                'number_of_inputs': None,
                'raw_replacement': '\\operatorname{Im}',
                'multi': False,
                'escape_name': '\\\\im',
                'regexp': '\\\\im(?![a-zA-Z])'
            }
        ]

        axmacro = Macro.Methods()
        axmacro.gather_macro(TEST_STRING)
        self.assertEqual(axmacro.macro_list[1].to_dict(), array_test[1])
        self.assertEqual(axmacro.macro_list[3].to_dict(), array_test[3])
        self.assertNotEqual(axmacro.macro_list[1].to_dict(), array_test[3])

    def test_remove_macro(self):
        axmacro = Macro.Methods()

        axmacro.gather_macro(TEST_STRING)

        string_new = axmacro.remove_macro(TEST_STRING, None, False)

        string_new_axessibility = axmacro.remove_macro(TEST_STRING, None, True)

        string_to_be = (
            r"\documentclass[11pt,reqno]{amsart}"
            "\n"            
            r"\begin{document}"
            "\n"
            r"\("
            "\n"
            r"\begin{tabular}{l}"
            "\n"
            r"\( \displaystyle (+\mathcal{L} )^{\displaystyle +\mathcal{L}}=+\mathcal{L} \)"
            "\n"
            r"\\"
            "\n"
            r"\(\displaystyle    (+\mathcal{L})^{-\mathcal{L}} =0\) "
            "\n"
            r"\end{tabular}"
            "\n"
            r"\)"
            "\n"
            r"\noindent"
            "\n"
            r"Student's surname and name \underline{\hspace{68.5ex}}"
            "\n"
            r"\vspace{1.5ex} "
            "\n"
            r"\noindent"
            "\n"
            r"Student's number \underline{\hspace{80ex}}"                    
            "\n"
            r"\vspace{8ex}"
            "\n"
            r"This formula is weird:"
            "\n"
            r"\[\operatorname{Im} \lim_{x\to\alpha} \gamma=\log_a_r \sum_{n = "
            r"\frac{1}{\{\mathcal{L}^2\}}}^{a} \mathcal{F}(\alpha) - 7 "
            r"+\frac{\frac{1}{\{\mathcal{L}^2\}}}{a} d\]"
            "\n"
            r"\noindent"
            "\n"
            r"\end{document}"
        )
        string_to_be_axessibility = (
            r"\documentclass[11pt,reqno]{amsart}"
            "\n"
            r"\usepackage{axessibility}"
            "\n"
            r"\begin{document}"
            "\n"
            r"\("
            "\n"
            r"\begin{tabular}{l}"
            "\n"
            r"\( \displaystyle (+\mathcal{L} )^{\displaystyle +\mathcal{L}}=+\mathcal{L} \)"
            "\n"
            r"\\"
            "\n"
            r"\(\displaystyle    (+\mathcal{L})^{-\mathcal{L}} =0\) "
            "\n"
            r"\end{tabular}"
            "\n"
            r"\)"
            "\n"
            r"\noindent"
            "\n"
            r"Student's surname and name \underline{\hspace{68.5ex}}"
            "\n"
            r"\vspace{1.5ex} "
            "\n"
            r"\noindent"
            "\n"
            r"Student's number \underline{\hspace{80ex}}"                    
            "\n"
            r"\vspace{8ex}"
            "\n"
            r"This formula is weird:"
            "\n"
            r"\[\operatorname{Im} \lim_{x\to\alpha} \gamma=\log_a_r \sum_{n = "
            r"\frac{1}{\{\mathcal{L}^2\}}}^{a} \mathcal{F}(\alpha) - 7 "
            r"+\frac{\frac{1}{\{\mathcal{L}^2\}}}{a} d\]"
            "\n"
            r"\noindent"
            "\n"
            r"\end{document}"
        )

        self.assertEqual(string_to_be, string_new)
        self.assertEqual(string_to_be_axessibility, string_new_axessibility)

    def test_remove_multiline_macro(self):
        axmacro = Macro.Methods()

        STRING = (r"\documentclass[11pt,reqno]{amsart}"
                  "\n"
                  r"\newcommand{\F}{\mathcal{F}} % trasformata di Fourier"
                  "\n"
                  r"\renewcommand{\L}{\mathcal{L}} % trasformata di Laplace"
                  "\n"
                  r"\newcommand{\LL}{\L^2} % trasformata di Laplace"
                  "\n"
                  r"\newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}"
                  "\n"
                  r"\DeclareMathOperator{\im}{Im}"
                  "\n"
                  r"\newcommand{\ztc}{\;|\ }"
                  "\n"
                  r"\newcommand\CM[1]{\par\vskip3mm\begin{center}\fbox{\parbox{5in}{#1}}\end{center}\par\vskip3mm}"
                  "\n"
                  r"\begin{document}"
                  "\n"
                  r"This is a very long text, with new lines and other stuff. For example an `accent or ' "
                  "\n"
                  "\n"
                  r"a weird new line. This should be untouched."
                  "\n"
                  r"\CM{"
                  "\n"
                  r"In questa notazione si noti:"
                  "\n"
                  r"\begin{itemize}"
                  "\n"
                  r"\item l'uso della parentesi graffa. La notazione $ \{\ \}  $ \`e una delle numerose notazioni"
                  r" matematiche che hanno pi\`u significati. In seguito vedremo altri usi della medesima notazione."
                  "\n"
                  r"\item Il simbolo ``$ \ztc $'' si legge ``tale che'' e pu\`o venir sostituito   "
                  "\n"
                  r"da due punti o anche da una virgola.  Talvolta viene sottinteso."
                  "\n"
                  r"\end{itemize}"
                  "\n"                  
                  r"}"
                  "\n"
                  "\end{document}")
        axmacro.gather_macro(STRING)
        string_new = axmacro.remove_macro(STRING, None, False)

        string_to_be = (r"\documentclass[11pt,reqno]{amsart}"                  
                  "\n"
                  r"\begin{document}"
                  "\n"
                  "This is a very long text, with new lines and other stuff. For example an `accent or ' "
                  "\n"
                  "\n"
                  "a weird new line. This should be untouched."
                  "\n"                        
                  r"\par\vskip3mm\begin{center}\fbox{\parbox{5in}{"
                  "\n"
                  r"In questa notazione si noti:"      
                  "\n"
                  r"\begin{itemize}"
                  "\n"
                  r"\item l'uso della parentesi graffa. La notazione \( \{ \}  \) \`e una delle numerose notazioni"
                  r" matematiche che hanno pi\`u significati. In seguito vedremo altri usi della medesima notazione."
                  "\n"
                  r"\item Il simbolo ``\( \;|  \)'' si legge ``tale che'' e pu\`o venir sostituito   "
                  "\n"
                  r"da due punti o anche da una virgola.  Talvolta viene sottinteso."
                  "\n"
                  r"\end{itemize}"
                  "\n"
                  r"}}\end{center}\par\vskip3mm"
                  "\n"
                  "\end{document}")


        string2 =(r"\documentclass[11pt,reqno]{amsart}"
                  "\n"
                  r"\newcommand{\F}{\mathcal{F}} % trasformata di Fourier"
                  "\n"
                  r"\renewcommand{\L}{\mathcal{L}} % trasformata di Laplace"
                  "\n"
                  r"\newcommand{\LL}{\L^2} % trasformata di Laplace"
                  "\n"
                  r"\newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}}"
                  "\n"
                  r"\DeclareMathOperator{\im}{Im}"
                  "\n"
                  r"\newcommand{\ztc}{\;|\ }"
                  "\n"
                  r"\newcommand\CM[1]{\par\vskip3mm\begin{center}\fbox{\parbox{5in}{#1}}\end{center}\par\vskip3mm}"
                  "\n"
                  r"\begin{document}"
                  "\n" 
                  r"\CM{Alcuni dei limiti elencati al paragrafo~\ref{cap2Sec:LImiti da ricordare} "
                  r"si possono riformulare come segue:"
                  "\n"
                  r"{\bf Ciascuno degli infiniti seguenti \`e di"
                  "\n"
                  r"{\rm ordine minore} del successivo: }"
                  "\n"
                  r"\["
                  "\n"
                  r"\{\log n\}\,,\quad \{n^b\}\,,\quad \{a^n\} \,,\quad (\{n!\} \,,\quad \{n^n\}"
                  "\n" 
                  r"\]"
                  "\n"
                  r"\medskip"
                  "\n"
                  r"\noindent"
                  "\n"
                  r"perch\'e"
                  "\n"
                  r"\medskip"
                  "\n"
                  r"\["
                  "\n"
                  r"\left\{\begin{array}"
                  "\n"
                  r"{ll}"
                  "\n"
                  r"\lim \frac{\log n}{n^a}=0 &\mbox{se $a>0$;}\\"
                  "\n"
                  r"\lim \frac{n^b}{a^n} =0&\mbox{se $a>1$, $b>0$;}"
                  "\n"
                  r"\end{array} \right. \qquad \qquad"
                  "\n"
                  r"\left\{\begin{array}"
                  "\n"
                  r"{ll}"
                  "\n"
                  r"\lim \frac{a^n}{n!}=0& \mbox{se $a>1$;}\\"
                  "\n"
                  r"\lim \frac{n!}{n^n}=0\,."
                  "\n"
                  r"\end{array} \right." 
                  "\n"
                  r"\]"
                  "\n"
                  r"}"
                  "\n"
                  r"\end{document}")
        string2be = (r"\documentclass[11pt,reqno]{amsart}"
                   "\n"
                   r"\begin{document}"
                   "\n"
                   r"\par\vskip3mm\begin{center}\fbox{\parbox{5in}{"
                   r"Alcuni dei limiti elencati al paragrafo~\ref{cap2Sec:LImiti da ricordare} "
                   r"si possono riformulare come segue:"
                   "\n"
                   r"{\bf Ciascuno degli infiniti seguenti \`e di"
                   "\n"
                   r"{\rm ordine minore} del successivo: }"
                   "\n"
                   r"\["
                   "\n"
                   r"\{\log n\}\,,\quad \{n^b\}\,,\quad \{a^n\} \,,\quad (\{n!\} \,,\quad \{n^n\}"
                   "\n"
                   r"\]"
                   "\n"
                   r"\medskip"
                   "\n"
                   r"\noindent"
                   "\n"
                   r"perch\'e"
                   "\n"
                   r"\medskip"
                   "\n"
                   r"\["
                   "\n"
                   r"\left\{\begin{array}"
                   "\n"
                   r"{ll}"
                   "\n"
                   r"\lim \frac{\log n}{n^a}=0 &\mbox{se \(a>0\);}\\"
                   "\n"
                   r"\lim \frac{n^b}{a^n} =0&\mbox{se \(a>1\), \(b>0\);}"
                   "\n"
                   r"\end{array} \right. \qquad \qquad"
                   "\n"
                   r"\left\{\begin{array}"
                   "\n"
                   r"{ll}"
                   "\n"
                   r"\lim \frac{a^n}{n!}=0& \mbox{se \(a>1\);}\\"
                   "\n"
                   r"\lim \frac{n!}{n^n}=0\,."
                   "\n"
                   r"\end{array} \right."
                   "\n"
                   r"\]"
                   "\n"
                   r"}}\end{center}\par\vskip3mm"  
                   "\n"  
                   r"\end{document}")
        axmacro.gather_macro(string2)
        string_new2 = axmacro.remove_macro(string2, None, False)
        print(string_new2)
        self.assertEqual(string2be, string_new2)
        self.assertEqual(string_to_be, string_new)


    def test_recursive_expansion(self):

        axmacro = Macro.Methods()

        axmacro.gather_macro(TEST_STRING)

        line = axmacro.recursive_expansion(r"$$\lim_{x\to\alpha} \gamma=\log_a_r " 
                                           r"\weird{\frac{1}{\{\LL\}}}{a}\alpha d$$"
                                           r"\`e una delle numerose notazioni"
                                           r" matematiche che hanno pi\`u significati. "
                                           r"In seguito vedremo altri usi della medesima notazione."
                                           )
        line_to_be = (r"$$\lim_{x\to\alpha} \gamma=\log_a_r \sum_{n = \frac{1}{\{\mathcal{L}^2\}}}^{a} \mathcal{F}(\alpha) - 7 "
                      r"+\frac{\frac{1}{\{\mathcal{L}^2\}}}{a} d$$"
                      r"\`e una delle numerose notazioni"
                      r" matematiche che hanno pi\`u significati. "
                      r"In seguito vedremo altri usi della medesima notazione."
                      )
        self.assertEqual(line_to_be,line)

    def test_multi_substitution_regexp(self):

        axmacro = Macro.Methods()

        macro = Macro.Macro({'command_type': 'newcommand',
                             'macro_name': '\\weird',
                             'separator_open': '{',
                             'separator_close': '}',
                             'number_of_inputs': '3',
                             'raw_replacement': '\\sum_{n = #1}^{#2} \\F(#3) - 7 +\\frac{#1}{#2}',
                            })

        string_to_test = axmacro.multi_substitution_regexp(macro,r"{\frac{1}{\{\LL\}}}{a}\alpha d$$")
        string_to_match = r"\sum_{n = \frac{1}{\{\LL\}}}^{a} \F(\alpha) - 7 +\frac{\frac{1}{\{\LL\}}}{a} d$$"

        self.assertEqual(string_to_test, string_to_match)

    def test_difficult_parsing_nested(self):
        string_to_parse = r"""
        \documentclass[11pt,reqno]{amsart} 
        \newcommand{\F}{\mathcal{F}} 
        \renewcommand{\L}{\mathcal{L}} 
        \newcommand{\LL}{\L^2} 
        \newcommand{\weird}[3]{\sum_{n = #1}^{#2} \F(#3) - 7 +\frac{#1}{#2}} \DeclareMathOperator{\im}{Im} 
        \newcommand{\ztc}{\;|\ } 
        \newcommand{\ZLA}{\label} 
        \newcommand{\ZIN}{\infty} 
        \newcommand\CM[1]{\par\vskip3mm\begin{center}\fbox{\parbox{5in}{#1}} \end{center}\par\vskip3mm}    
        \begin{document} 
        \begin{center}
            \begin{table}
                [h]\caption{\ZLA{cap2:table:finaleRegCalcFORIND}Regole di calcolo e forme indeterminate} \smallskip 
                \begin{center}
                    \hskip -7cm\parbox{3in}{ 
                    \begin{tabular}
                        [h]{||| c|| c| c |||} \hline\hline\hline &&\\
                        Regole & $ +\ZIN +\ZIN =+\ZIN $& $ -\ZIN -\ZIN =-\ZIN $\\
                        &&\\
                        \cline{2-3} &&\\
                        & $
                        \begin{array}{l}(+\ZIN)(+\ZIN)=+\ZIN\\
                        (-\ZIN)(-\ZIN)=+\ZIN\end{array}$& $(-\ZIN)(+\ZIN)=-\ZIN=(+\ZIN)(-\ZIN)$ \\
                        && \\
                        &&\\
                        \cline{2-3} &&\\
                        & $\displaystyle \left | \frac{\displaystyle \pm\ZIN}{\displaystyle 0}\right |=+\ZIN $ & $\displaystyle \frac{\displaystyle 0} {\displaystyle \pm\ZIN}=0 $ \\
                        &&\\
                        \cline{2-3} &&\\
                        & $ 
                        \begin{tabular}
                            {c} $l+(+\ZIN)=l+\ZIN=+\ZIN$\\
                            $l+(-\ZIN)=l-\ZIN=-\ZIN$ 
                        \end{tabular}
                        $ & $ l(+\ZIN)=\left\{ 
                        \begin{tabular}
                            {cl} $ +\ZIN $&\mbox{se $l>0$}\\
                            $ -\ZIN$ &\mbox{se $l<0$} 
                        \end{tabular}
                        \right. $ \\
                        
                        \cline{2-3} &&\\
                        
                        & & \\
                        & 
                        \begin{tabular}
                            {l} $ \displaystyle 0 ^{\displaystyle +\ZIN}=0 $ \\
                            $ 0^{-\ZIN}=+\ZIN $ 
                        \end{tabular}
                        & $ 
                        \begin{tabular}
                            {l} $ \displaystyle (+\ZIN )^{\displaystyle +\ZIN}=+\ZIN $ \\
                            $\displaystyle (+\ZIN)^{-\ZIN} =0$ 
                        \end{tabular}
                        $ \\
                        
                        && \\
                        \hline\hline &&\\
                        $
                        \begin{array}{l}
                            {\rm Forme} \\
                            {\rm indeterminate} 
                        \end{array}
                        $ & $ +\ZIN - \ZIN $ & $ 0\cdot(\pm\ZIN) $ \\
                        &&\\
                        \cline{2-3} &&\\
                        & $\displaystyle \frac{\displaystyle \pm\ZIN}{\displaystyle \pm\ZIN} $ & $\displaystyle \frac{\displaystyle 0}{\displaystyle 0} $ \\
                        &&\\
                        \cline{2-3} &&\\
                        & $\displaystyle 0^{\displaystyle 0} $ \qquad $\displaystyle (+\ZIN)^{\displaystyle 0} $ & $\displaystyle 1^{\displaystyle \pm\ZIN}$ \\
                        &&\\
                        \hline\hline\hline
                    \end{tabular}
                    }
                \end{center}
            \end{table}
        \end{center}
        \end{document}
        """
        string_to_be = r"""
        \documentclass[11pt,reqno]{amsart} 
        \begin{document} 
        \begin{center}
            \begin{table}
                [h]\caption{\label{cap2:table:finaleRegCalcFORIND}Regole di calcolo e forme indeterminate} \smallskip 
                \begin{center}
                    \hskip -7cm\parbox{3in}{ 
                    \begin{tabular}
                        [h]{||| c|| c| c |||} \hline\hline\hline &&\\
                        Regole & \( +\infty +\infty =+\infty \)& \( -\infty -\infty =-\infty \)\\
                        &&\\
                        \cline{2-3} &&\\
                        & \(
                        \begin{array}{l}(+\infty)(+\infty)=+\infty\\
                        (-\infty)(-\infty)=+\infty\end{array}\)& \((-\infty)(+\infty)=-\infty=(+\infty)(-\infty)\) \\
                        && \\
                        &&\\
                        \cline{2-3} &&\\
                        & \(\displaystyle \left | \frac{\displaystyle \pm\infty}{\displaystyle 0}\right |=+\infty \) & \(\displaystyle \frac{\displaystyle 0} {\displaystyle \pm\infty}=0 \) \\
                        &&\\
                        \cline{2-3} &&\\
                        & \( 
                        \begin{tabular}
                            {c} \(l+(+\infty)=l+\infty=+\infty\)\\
                            \(l+(-\infty)=l-\infty=-\infty\) 
                        \end{tabular}
                        \) & \( l(+\infty)=\left\{ 
                        \begin{tabular}
                            {cl} \( +\infty \)&\mbox{se \(l>0\)}\\
                            \( -\infty\) &\mbox{se \(l<0\)} 
                        \end{tabular}
                        \right. \) \\
                        
                        \cline{2-3} &&\\
                        
                        & & \\
                        & 
                        \begin{tabular}
                            {l} \( \displaystyle 0 ^{\displaystyle +\infty}=0 \) \\
                            \( 0^{-\infty}=+\infty \) 
                        \end{tabular}
                        & \( 
                        \begin{tabular}
                            {l} \( \displaystyle (+\infty )^{\displaystyle +\infty}=+\infty \) \\
                            \(\displaystyle (+\infty)^{-\infty} =0\) 
                        \end{tabular}
                        \) \\
                        
                        && \\
                        \hline\hline &&\\
                        \(
                        \begin{array}{l}
                            {\rm Forme} \\
                            {\rm indeterminate} 
                        \end{array}
                        \) & \( +\infty - \infty \) & \( 0\cdot(\pm\infty) \) \\
                        &&\\
                        \cline{2-3} &&\\
                        & \(\displaystyle \frac{\displaystyle \pm\infty}{\displaystyle \pm\infty} \) & \(\displaystyle \frac{\displaystyle 0}{\displaystyle 0} \) \\
                        &&\\
                        \cline{2-3} &&\\
                        & \(\displaystyle 0^{\displaystyle 0} \) \qquad \(\displaystyle (+\infty)^{\displaystyle 0} \) & \(\displaystyle 1^{\displaystyle \pm\infty}\) \\
                        &&\\
                        \hline\hline\hline
                    \end{tabular}
                    }
                \end{center}
            \end{table}
        \end{center}
        \end{document}"""

        axmacro = Macro.Methods()

        axmacro.gather_macro(string_to_parse)

        string_parsed = axmacro.remove_macro(string_to_parse, None, False);

        self.assertEqual(string_to_be, string_parsed)
        print(string_parsed)


class AxessCleanerTextMethods(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_accessibility(self):

        line_no_package = r"\begin{document}"

        line_package = (r"\usepackage{axessibility}" 
                        "\n"
                        r"\begin{document}")

        text_methods = Text.Methods()

        self.assertEqual(text_methods
                         .add_axessibility(line_no_package)
                         ,
                         line_package)

    def test_find_accessibility(self):
        line_package = '\\usepackage{axessibility} %axessibility package installed'

        line_no_package = '\\usepackage{amsmath} %math'

        text_methods = Text.Methods()

        self.assertEqual(text_methods.find_axessibility(line_package), True)
        self.assertEqual(text_methods.find_axessibility(line_no_package), False)

    def test_remove_dollars_from_text_env(self):
        line_to_sub = r'Test $ f(x)+g(x) = F(x) \mbox{ where $f(x)$ and $g(x)$ are smooth} $'

        subbed_line = r'Test $ f(x)+g(x) = F(x) \mbox{ where \(f(x)\) and \(g(x)\) are smooth} $'

        line_to_sub_2 = r'k\mapsto n(k) \quad \mbox{ossia la successione$ \{n_k\} $ \`e {\bf strettamente crescente.}}'

        subbed_line_2 = r'k\mapsto n(k) \quad \mbox{ossia la successione\( \{n_k\} \) \`e {\bf strettamente crescente.}}'

        line_3 = r"&&= \frac{A_1}{x-x_0}+\frac{,\mbox{d}}{,\mbox{d} x}\left \{\frac{-A_2}{x-x_0}+\cdots+\frac{A_n}{(1-n)}\frac{1}{(x-x_0)^{n-1}}\right\}\,."
        sub_3 =  r"&&= \frac{A_1}{x-x_0}+\frac{,\mbox{d}}{,\mbox{d} x}\left \{\frac{-A_2}{x-x_0}+\cdots+\frac{A_n}{(1-n)}\frac{1}{(x-x_0)^{n-1}}\right\}\,."
        rm = Text.Methods().remove_dollars_from_text_env

        self.assertEqual(subbed_line, rm(line_to_sub))
        self.assertEqual(subbed_line_2, rm(line_to_sub_2))
        self.assertEqual(sub_3, rm(line_3))

    def test_remove_inline_dls(self):
        line_to_sub = r'Test $ f(x)+g(x) = F(x) \mbox{ where $f(x)$ and $g(x)$ are smooth} $'

        subbed_line = r'Test \( f(x)+g(x) = F(x) \mbox{ where \(f(x)\) and \(g(x)\) are smooth} \)'

        line_to_sub_dd = r'$$\im \lim_{x\to\alpha} $$ $$\gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d$$'

        subbed_line_dd = r'\[\im \lim_{x\to\alpha} \] \[\gamma=\log_a_r \weird{\frac{1}{\{\LL\}}}{a}\alpha d\]'

        rm = Text.Methods().remove_dollars_from_text_env
        rm_i = Text.Methods().remove_inline_dls
        self.assertEqual(subbed_line, rm_i(rm(line_to_sub),'$'))
        self.assertEqual(subbed_line_dd, rm_i(line_to_sub_dd, '$$'))
        with self.assertRaises(ValueError):
            rm_i('string','££')

    def test_count_symbols_in_string(self):
        string = (r"$"
                  r"\begin{tabular}{l}"
                  r"$ \displaystyle (+\ZIN )^{\displaystyle +\ZIN}=+\ZIN $"
                  r"\\"
                  r"$\displaystyle    (+\ZIN)^{-\ZIN} =0$ "
                  r"\end{tabular}"
                  r"$")
        string_dd = (r"$$"
                  r"\begin{tabular}{l}"
                  r"$ \displaystyle (+\ZIN )^{\displaystyle +\ZIN}=+\ZIN $"
                  r"\\"
                  r"$\displaystyle    (+\ZIN)^{-\ZIN} =0$ "
                  r"\end{tabular}"
                  r"$$")

        self.assertEqual(6, Text.Methods().count_symbols_in_string(string,'$'))
        self.assertEqual(2, Text.Methods().count_symbols_in_string(string_dd, '$$'))
        self.assertEqual(0, Text.Methods().count_symbols_in_string(string, '$$'))

    def test_remove_sparse_dl(self):
        string = r"$& $(-\infty)(+\infty)=-\infty=(+\infty)(-\infty)$ \\"
        string_clean = r"\)& \((-\infty)(+\infty)=-\infty=(+\infty)(-\infty)\) \\"
        Text.Methods().dl_open = 1
        self.assertEqual(string_clean, Text.Methods().remove_sparse_dl(string))


if __name__ == '__main__':
    unittest.main()
