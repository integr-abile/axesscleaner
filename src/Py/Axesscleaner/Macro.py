import re
import ply.lex


class Macro:

    START_PATTERN = 'egin{document}'
    END_PATTERN = 'nd{document}'

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

    @staticmethod
    def gather_macro(strz):
        """
        :param strz: a text line
        :return: list of dict

        This method searches for defs, newcommands, edef, gdef,xdef, DeclareMathOperators and renewcommand
            and gets the (dict) macro structure out of it. Number
        """

        # By default the macro reads any line

        MACRO_DICTIONARY = []

        should_parse = True

        # parse preamble
        for ii, LINE in enumerate(strz.split('\n')):
            if should_parse:
                if re.search(Macro.START_PATTERN, LINE):

                    """ 
                        if the parser finds the beginning of the document, it stops the parsing. 
                        No macro allowed inside \begin{document}..\end{document}
                    """
                    should_parse = False
                else:
                    # perform the parsing
                    result = Macro.parse_macro_structure(LINE)

                    # If the dictionary has a macro name and a replacement content, then it performs the result.
                    if result.get('macro_name', None) is not None and result.get('raw_replacement', None) is not None:
                        MACRO_DICTIONARY.append(result)
            else:
                if re.search(Macro.END_PATTERN, LINE):

                    # If we ended the preamble, we quit the loop. If not, we go on.
                    break
                else:
                    pass
        return MACRO_DICTIONARY

    @staticmethod
    def get_expanded_macro(array):
        """
            :param ''
            :return: list

            It returns a list with all the expanded macros, ready to be subbed. This is done by calling the
            method:build_subs_regexp

        """
        subs_regexp = []
        for reg in array:
            expanded_regexp = Macro.enrich_regexp(reg)
            if expanded_regexp:
                subs_regexp.append(expanded_regexp)
        return subs_regexp

    @staticmethod
    def remove_macro(st, output_file, macro_array):
        """
        :param st: string where macros have to be removed
        :param output_file: name of output file
        :param macro_array: array of macros
        :return: ''
        It performs the actual removal of the macros by looping through all the lines and applying the recursive expansion
        between \begin{document}, \end{document}

        """
        # getting the list of expanded macros

        subs_regexp = Macro.get_expanded_macro(macro_array)

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
                if re.search(Macro.END_PATTERN, reading_line):
                    final_doc.append(reading_line)
                    break
                else:
                    # Perform substitutions
                    try:
                        reading_line = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]',
                                            '',
                                              Macro.recursive_expansion(
                                                reading_line,
                                                subs_regexp
                                                )
                                            )
                    except Exception as e:
                        print(e, reading_line)
                        break

            else:
                if re.search(Macro.START_PATTERN, reading_line):
                    should_substitute = True
                else:
                    pass
            if not reading_line.isspace():
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
        regexp = r"\\(.*command|DeclareMathOperator|def|edef|xdef|gdef)({|)(\\[a-zA-Z]+)(}|)(\[([0-9])\]|| +){(.*(?=\}))\}.*$"
        result = re.search(regexp, ln)
        if result:
            regex = r"\\([[:blank:]]|)(?![a-zA-Z])"
            macro_structure = {
                'command_type': result.group(1),
                'macro_name': result.group(3),
                'separator_open': result.group(2),
                'separator_close': result.group(4),
                'number_of_inputs': result.group(6),
                'raw_replacement': re.sub(regex, '', result.group(7)),
            }
            return macro_structure
        else:
            return {}

    @staticmethod
    def enrich_regexp(reg):
        """
            :param reg: regexp dict
            :return: sub: enriched regexp dict.

            This method creates the replacement text for the macro, determines if the input is single or multi,
            avoids declarations macro.

        """
        if re.search('declare', reg["command_type"]):

            pass
        else:
            sub = {'sub': reg["raw_replacement"], 'reg': '\\' + reg["macro_name"], "macro": reg}
            if not reg["number_of_inputs"]:
                # The macro has no inputs
                sub['multi'] = False
            else:
                # The macro has one or more inputs
                sub['multi'] = True
            return sub

    @staticmethod
    def recursive_expansion(lin, available_macros):
        """

        :param lin: line of text, string
        :param available_macros:  regexp, dict
        :return:lin, a string with the macro subbed.

        The method takes the line,loops on all the available macros recorded and determines if those are present in the line
        If so, there are two cases. A) The macro has no input B) The macro has one or more inputs. In the first case, the
        replacement text is created directly. In the second case, multi_substitution_regexp is called.

        """
        for subs in available_macros:
            search = re.search(subs["reg"], lin)
            if not search:
                continue
            else:
                if subs["multi"] is True:
                    to_sub = subs["reg"] + '\s*(.*$)'
                    search_full = re.search(to_sub, lin)
                    subs["sub"] = Macro.multi_substitution_regexp(subs, search_full.group(1))
                else:
                    to_sub = subs["reg"] + '(?![a-zA-Z])'
                try:
                    lin = re.sub(to_sub, re.sub(r'([\" \' \\\ ])', r'\\\1', subs["sub"]), lin)
                except Exception as e:
                    print(e, lin)
        for subs in available_macros:
            if not (not (re.search(subs["reg"], lin))):
                return Macro.recursive_expansion(lin, available_macros)
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

        while text_cursor < len(textafter) and len(input_list) < int(rexpr["macro"]["number_of_inputs"]):
            character = textafter[text_cursor]

            # check if the char is an open separator
            if character == rexpr["macro"]["separator_open"]:
                # check if the count_open is equal to count close
                if count_close == count_open:
                    # if so, the separator should not be added as input replacement. we just update the count
                    count_open += 1
                else:
                    # if not, two cases. Open and close separator are the same
                    if character == rexpr["macro"]["separator_close"]:
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
                if character == rexpr["macro"]["separator_close"]:
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
        for j, strings in enumerate(input_list):
            rexpr['sub'] = re.sub('#' + str(j + 1), re.sub(r'([\" \' \\\ ])', r'\\\1', strings), rexpr['sub'])

        # We finish by adding the part we edited and the rest of the line.
        replacement_text: str = rexpr['sub']+textafter[text_cursor:]
        return replacement_text
