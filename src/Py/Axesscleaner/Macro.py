import re
import ply.lex
from Axesscleaner import Text


class Macro:

    def __init__(self, macro_dict):
        self.command_type = macro_dict.get("command_type" or "")
        self.macro_name = macro_dict.get("macro_name" or "")
        self.separator_open = macro_dict.get("separator_open" or "")
        self.separator_close = macro_dict.get("separator_close" or "")
        self.number_of_inputs = macro_dict.get("number_of_inputs" or "")
        self.raw_replacement = self.enhance_raw_replacement(macro_dict.get("raw_replacement" or ""))

        if not self.number_of_inputs:
            # The macro has no inputs
            self.multi = False
        else:
            # The macro has one or more inputs
            self.multi = True

        if self.is_not_empty():
            self.regexp = self.enrich_macro()
            self.escape_name = '\\' + self.macro_name
        else:
            self.escape_name = None
            self.regexp = None

    def is_not_empty(self):

        return self.macro_name is not None and self.raw_replacement is not None

    def enrich_macro(self):
        """
            This method returns creates the regexp to search on the text to parse the  macro

                """
        if self.multi is True:
            # The macro has no inputs
            rxp = '\\' + self.macro_name + '\s*(.*$)'
        else:
            # The macro has one or more inputs
            rxp = '\\' + self.macro_name + '(?![a-zA-Z])'
        return rxp

    def enhance_raw_replacement(self, rr):

        if self.command_type == 'DeclareMathOperator':
            return '\\operatorname{'+rr+'}'
        else:
            return rr

    def to_dict(self):

        return {
            "command_type": self.command_type,
            "macro_name": self.macro_name,
            "separator_open": self.separator_open,
            "separator_close": self.separator_close,
            "number_of_inputs": self.number_of_inputs,
            "raw_replacement": self.raw_replacement,
            "multi": self.multi,
            "escape_name": self.escape_name,
            "regexp": self.regexp,
        }


class Methods:

    def __init__(self):
        self.macro_list = []
        self.START_PATTERN = 'egin{document}'
        self.END_PATTERN = 'nd{document}'
        self.axessibility_found = False
        self.text_methods = Text.Methods()

    @staticmethod
    def strip_comments(source):
        # Usage
        # python stripcomments.py input.tex > output.tex
        # python stripcomments.py input.tex -e encoding > output.tex

        # modified from https://gist.github.com/amerberg/a273ca1e579ab573b499

        # Usage
        # python stripcomments.py input.tex > output.tex
        # python stripcomments.py input.tex -e encoding > output.tex

        # Modification:
        # 1. Preserve "\n" at the end of line comment
        # 2. For \makeatletter \makeatother block, Preserve "%"
        #    if it is actually a comment, and trim the line
        #    while preserve the "\n" at the end of the line.
        #    That is because remove the % some time will result in
        #    compilation failure.
        tokens = (
            'PERCENT', 'BEGINCOMMENT', 'ENDCOMMENT',
            'BACKSLASH', 'CHAR', 'BEGINVERBATIM',
            'ENDVERBATIM', 'NEWLINE', 'ESCPCT',
            'MAKEATLETTER', 'MAKEATOTHER',
        )
        states = (
            ('makeatblock', 'exclusive'),
            ('makeatlinecomment', 'exclusive'),
            ('linecomment', 'exclusive'),
            ('commentenv', 'exclusive'),
            ('verbatim', 'exclusive')
        )

        # Deal with escaped backslashes, so we don't
        # think they're escaping %
        def t_BACKSLASH(t):
            r"\\\\"
            return t

        # Leaving all % in makeatblock
        def t_MAKEATLETTER(t):
            r"\\makeatletter"
            t.lexer.begin("makeatblock")
            return t

        # One-line comments
        def t_PERCENT(t):
            r"\%"
            t.lexer.begin("linecomment")

        # Escaped percent signs
        def t_ESCPCT(t):
            r"\\\%"
            return t

        # Comment environment, as defined by verbatim package
        def t_BEGINCOMMENT(t):
            r"\\begin\s*{\s*comment\s*}"
            t.lexer.begin("commentenv")

        # Verbatim environment (different treatment of comments within)
        def t_BEGINVERBATIM(t):
            r"\\begin\s*{\s*verbatim\s*}"
            t.lexer.begin("verbatim")
            return t

        # Any other character in initial state we leave alone
        def t_CHAR(t):
            r"."
            return t

        def t_NEWLINE(t):
            r"\n"
            return t

        # End comment environment
        def t_commentenv_ENDCOMMENT(t):
            r"\\end\s*{\s*comment\s*}"
            # Anything after \end{comment} on a line is ignored!
            t.lexer.begin('linecomment')

        # Ignore comments of comment environment
        def t_commentenv_CHAR(t):
            r"."
            pass

        def t_commentenv_NEWLINE(t):
            r"\n"
            pass

        # End of verbatim environment
        def t_verbatim_ENDVERBATIM(t):
            r"\\end\s*{\s*verbatim\s*}"
            t.lexer.begin('INITIAL')
            return t

        # Leave contents of verbatim environment alone
        def t_verbatim_CHAR(t):
            r"."
            return t

        def t_verbatim_NEWLINE(t):
            r"\n"
            return t

        # End a % comment when we get to a new line
        def t_linecomment_ENDCOMMENT(t):
            r"\n"
            t.lexer.begin("INITIAL")

            # Newline at the end of a line comment is presevered.
            return t

        # Ignore anything after a % on a line
        def t_linecomment_CHAR(t):
            r"."
            pass

        def t_makeatblock_MAKEATOTHER(t):
            r"\\makeatother"
            t.lexer.begin('INITIAL')
            return t

        def t_makeatblock_BACKSLASH(t):
            r"\\\\"
            return t

        # Escaped percent signs in makeatblock
        def t_makeatblock_ESCPCT(t):
            r"\\\%"
            return t

        # presever % in makeatblock
        def t_makeatblock_PERCENT(t):
            r"\%"
            t.lexer.begin("makeatlinecomment")
            return t

        def t_makeatlinecomment_NEWLINE(t):
            r"\n"
            t.lexer.begin('makeatblock')
            return t

        # Leave contents of makeatblock alone
        def t_makeatblock_CHAR(t):
            r"."
            return t

        def t_makeatblock_NEWLINE(t):
            r"\n"
            return t

        # For bad characters, we just skip over it
        def t_ANY_error(t):
            t.lexer.skip(1)

        lexer = ply.lex.lex()
        lexer.input(source)
        return u"".join([tok.value for tok in lexer])

    def gather_macro(self, strz):
        """
        :param strz: a text line
        :return: list of dict

        This method searches for defs, newcommands, edef, gdef,xdef, DeclareMathOperators and renewcommand
            and gets the (dict) macro structure out of it. Number
        """

        should_parse = True
        temp_array = []
        # parse preamble
        for ii, LINE in enumerate(strz.split('\n')):
            if should_parse:
                if re.search(self.START_PATTERN, LINE):

                    """ 
                        if the parser finds the beginning of the document, it stops the parsing. 
                        No macro allowed inside \begin{document}..\end{document}
                    """
                    should_parse = False
                    break
                else:
                    # perform the parsing
                    macro = self.parse_macro_structure(LINE)

                    # If the dictionary has a macro name and a replacement content, then it performs the result.
                    if macro.is_not_empty():
                        temp_array.append(macro)
                    if self.text_methods.find_axessibility(LINE):
                        print('axessibility package already included')
                        self.axessibility_found = True
                    else:
                        pass
            else:
                pass
        self.macro_list.extend(temp_array)

    def remove_macro(self, st, output_file, add_package):
        """
        :param st: string where macros have to be removed
        :param output_file: name of output file
        :param macro_array: array of macros
        :return: ''
        It performs the actual removal of the macros by looping through all the lines and applying the recursive expansion
        between \begin{document}, \end{document}
        If the axessibility package is not found, it adds it to the text.
        """
        # by default, we set should_sobstitute as false,
        # we want to perform the substitution only between begin/end document.

        should_substitute = False

        # list that will contain the full file (line by line)

        final_doc = []

        for ii, reading_line in enumerate(st.split('\n')):
            """
                If we are inside the document, it first checks if we reached the end,
                if not, it performs the substitution by also escaping space charachters. 
                If we are outside, we check if we reached the beginning of it. 
                When the docs ends, it stops by default. 
            """
            if should_substitute:
                if re.search(self.END_PATTERN, reading_line):
                    final_doc.append(reading_line)
                    break
                else:
                    # Perform substitutions
                    try:
                        reading_line = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]',
                                              '',
                                              self.recursive_expansion(
                                                reading_line
                                                )
                                            )
                    except Exception as e:
                        print(e, reading_line)
                        break

            else:
                if re.search(self.START_PATTERN, reading_line):
                    should_substitute = True
                    if self.axessibility_found is False and add_package is True:
                        reading_line = self.text_methods.add_axessibility(reading_line)
                        self.axessibility_found = True
                else:
                    pass
            if not reading_line.isspace():
                regexp = r"\\(.*command|DeclareMathOperator|def|edef|xdef|gdef)({|)(\\[a-zA-Z]+)(}|)(\[([0-9])\]|| +){(.*(?=\}))\}.*$"
                result = re.search(regexp, reading_line)
                if result is None:
                    final_doc.append(reading_line)

        if output_file is not None:
            with open(output_file, 'w') as o:
                for final_line in final_doc:
                    if final_line.rstrip():
                        o.write(final_line + '\n')
            return ''
        else:
            final_string = ''
            for final_line in final_doc:
                if final_line.rstrip():
                    final_string += final_line + '\n'
            return final_string

    @staticmethod
    def parse_macro_structure(ln):
        """
        :param ln: a text line
        :return: dict

        It returns a (potentially empty) dictionary with the structure (see below) of the macro inside the line
        """
        regexp = r"\\(.*command|DeclareMathOperator|def|edef|xdef|gdef)({|)(\\[a-zA-Z]+)(}|)(\[([0-9])\]|| +)({|#)(.*(?=(\}|\#)))(\#|\}).*$"
        result = re.search(regexp, ln)
        if result:
            regex = r"\\([[:blank:]]|)(?![a-zA-Z])"
            macro_structure = Macro({
                'command_type': result.group(1),
                'macro_name': result.group(3),
                'separator_open': result.group(7),
                'separator_close': result.group(9),
                'number_of_inputs': result.group(6),
                'raw_replacement': re.sub(regex, '', result.group(8)),
            })
            return macro_structure
        else:
            return Macro({})

    def recursive_expansion(self, lin):
        """

        :param lin: line of text, string
        :return:lin, a string with the macro subbed.

        The method takes the line,loops on all the available macros recorded and determines if those are present in the line
        If so, there are two cases. A) The macro has no input B) The macro has one or more inputs. In the first case, the
        replacement text is created directly. In the second case, multi_substitution_regexp is called.

        """
        for subs in self.macro_list:
            search = re.search(subs.escape_name, lin)
            if not search:
                continue
            else:
                if subs.multi is True:
                    search_full = re.search(subs.regexp, lin)
                    to_sub = self.multi_substitution_regexp(subs, search_full.group(1))
                else:
                    to_sub = subs.raw_replacement
                try:
                    lin = re.sub(subs.regexp, re.sub(r'([\" \' \\\ ])', r'\\\1', to_sub), lin)
                except Exception as e:
                    print(e, lin)
        for subs in self.macro_list:
            if not (not (re.search(subs.escape_name, lin))):
                return self.recursive_expansion(lin)
            else:
                continue
        return lin

    @staticmethod
    def multi_substitution_regexp(rexpr, textafter):
        """
        :param rexpr: dict
        :param textafter: str
        :return: replacement_text: str

        The method takes the string after the macro's name and tries to parse it. More explanations in the code.
        1) searches for the open-separator and increase the respective counter (count_open)
        2) searches for escaped separators and characters and adds them to the temp_string
        3) as soon as it encounters another open separator, it treats it as a text to be added while increasing count_open
        4) if it's a regular char, there are two bea
        5) if it encounters a closing separator, it increases count_close. If count close is equal to count_open, the
        program closed as many separators as opened. So, it
        """

        count_open: int = 0                     # counts the open-separators

        count_close: int = 0                    # counts the open-separators

        input_list: int = []                    # list of parsed arguments

        text_cursor: int = 0                   # int cursor, signals the position in the text.

        temp_text: str = ''                     # Temporary string

        # Loop on every char of textafter.
        # Exits when the cursor is at the end of the string or the number of inputs is reached.

        while text_cursor < len(textafter) and len(input_list) < int(rexpr.number_of_inputs):
            character = textafter[text_cursor]

            # check if the char is an open separator
            if character == rexpr.separator_open:
                # check if the count_open is equal to count close
                if count_close == count_open:
                    # if so, the separator should not be added as input replacement. we just update the count
                    count_open += 1
                else:
                    # if not, two cases. Open and close separator are the same
                    if character == rexpr.separator_close:
                        # update the close count
                        count_close += 1

                        # check if the count_open is equal to count close.
                        # f so, add the temp_text to the input and reset temp_text
                        if count_close == count_open:
                            input_list.append(temp_text)
                            temp_text = ''
                        else:
                            # if not, just add it as a character
                            temp_text += character
                    else:
                        # the character is an open separator, not a closing one. And  count_open is NOT equal to count close
                        # Hence, it is part of the input. We add it to the text while updating the count.
                        count_open += 1
                        temp_text += character
            # Character is not an open separator
            else:
                # Character is a close separator,we act as above.
                if character == rexpr.separator_close:
                    count_close += 1
                    if count_close == count_open:
                        input_list.append(temp_text)
                        temp_text = ''
                    else:
                        temp_text += character
                # Character is not an open or a close separator
                else:
                    # Character is an escape
                    if character == "\\":
                        # We search for the first non-letter
                        cursor_end = re.search('(?![a-zA-Z])', textafter[text_cursor+1:]).start() or 1
                        # we add the escape plus either the first character
                        # or a every char until the first non letter one (excluded).
                        # Example: \\{a -> \\{, \\alpha+ ->\\alpha
                        start_pattern = text_cursor
                        end_pattern = int(start_pattern) + max(cursor_end, 1)+1
                        pattern = textafter[start_pattern:end_pattern]
                        # we add it to the input and we move the cursor to the last char we took.
                        temp_text += pattern
                        text_cursor = int(end_pattern)-1
                    else:
                        # With no escape, we just add the char.
                        temp_text += character

                    # count close is equal to count open, we are "outside" the separators
                    if count_close == count_open:
                        input_list.append(temp_text)
                        temp_text = ''
            text_cursor += 1
        # perform the actual substitution. Each #1,#2,#3,... is subbed with the content of input_list.

        replacement_text: str = rexpr.raw_replacement

        for j, strings in enumerate(input_list):
            replacement_text = re.sub('#' + str(j + 1), re.sub(r'([\" \' \\\ ])', r'\\\1', strings), replacement_text)

        # We finish by adding the part we edited and the rest of the line.
        replacement_text += textafter[text_cursor:]
        return replacement_text