import re


class Methods:

    def __init__(self):
        self.dl_open = [0]
        self.dd_dls_open = [0]
        self.newEnv = 0
        self.line_dl_open = 0
        self.line_ddl_open = 0

    @staticmethod
    def find_axessibility(line):
        if re.search('sepackage( |){axessibility}', line):
            return True
        else:
            return False
    @staticmethod
    def add_axessibility(line):
        return re.sub('\\\\begin{document}', '\\usepackage{axessibility}\n\\\\begin{document}', line)

    def remove_dollars_from_text_env(self, line):
        """
        :param line: a text line
        :return: temp: clean string

        It transforms $<stuff, but no $>$ in \(<stuff, but no $>\) only if the pattern is
        * in one single line
        * is included in one of the following environments: mbox, mathrm, textrm

        Example
            1 ) The routine leaves the string untouched:

                input : This is a Formula: $3+4$
                output  This is a Formula: $3+4$
            2) The routine modifies the string

                input : Test $ f(x)+g(x) = F(x) \mbox{ where $f(x)$ and $g(x)$ are smooth} $
                output: Test $ f(x)+g(x) = F(x) \mbox{ where \(f(x)\) and \(g(x)\) are smooth} $



        """
        regex = r"(?:\\)(?:mbox|textrm|mathrm)(?:\s*)(?:\{)(.*?)(?<!\\)(?:\})"
        outer = re.findall(regex, line)
        if outer is not None and len(outer) > 0:
            to_sub = self.remove_inline_dls(outer[0], '$')
            subbed = re.sub(re.escape(outer[0]), re.sub(r'([\\|\"])', r'\\\1', to_sub), line)
            return re.sub(
                r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]',
                '',
                subbed)
        else:
            return line

    def remove_inline_dls(self, line, sym):

        """
                :param line: a text line
                :param sym: simbol to be removed
                :return: temp: clean string

                It transforms
                * $<stuff, but no $>$ in \(<stuff, but no $>\) or
                * $$<stuff, but no $>$$ in \[<stuff, but no $>\]
                only if the pattern is in one single line


                Example
                    1 ) The routine leaves the string untouched:

                        input : This is a Formula: $3+4$
                        output  This is a Formula: \(3+4\)

        """

        if sym == '$':
            regex = r"(?<!\$)\$([^\$].*?)\$"
            sym_to_open = '\('
            sym_to_close = '\)'
        else:
            if sym == '$$':
                regex = r"\$\$(.*?)\$\$"
                sym_to_open = '\['
                sym_to_close = '\]'
            else:
                raise ValueError('Supported symbols:"$" and "$$"')

        temp = '' + line
        count = self.count_symbols_in_string(line, sym) % 2
        # You can manually specify the number of replacements by changing the 4th argument

        search_form = re.search(regex, temp)
        if search_form and count == 0:
            try:
                to_be_subbed = search_form.group(0)
                to_sub = sym_to_open + search_form.group(1) + sym_to_close
                temp = temp.replace(to_be_subbed, to_sub)
                if re.search(regex, temp) is not None:
                    return self.remove_inline_dls(temp, sym)
                else:
                    return temp
            except Exception as e:
                print(e)
        else:
            return temp

    def count_symbols_in_string(self, lin, symbol):
        """

        :param lin: line of text, string
        :return:count, number of symbols in string.

        The method takes the line and counts the number of occurences of the character to sub.

        """
        if symbol == '$':
            return len(re.findall(r"(?<!\$)\$", lin))
        else:
            if symbol == '$$':
                return len(re.findall(re.escape("$$"), lin))
            else:
                raise ValueError('Supported symbols:"$" and "$$"')

    def find_open_dls(self, sym):
        if sym == '$':
            if self.dl_open[self.newEnv] % 2 == 0 and self.dl_open[self.newEnv] > 0:
                return True
            else:
                return False
        else:
            if sym == '$$':
                if self.dd_dls_open[self.newEnv] % 2 == 0 and self.dd_dls_open[self.newEnv] > 0:
                    return True
                else:
                    return False
            else:
                raise ValueError('Supported symbols:"$" and "$$"')

    def search_for_environments(self, line):

        regex_plus = r"\\begin({|)(array|tabular)(}|).*$"
        regex_minus = r"\\end({|)(array|tabular)(}|).*$"
        if re.findall(regex_minus, line):
            self.dl_open.pop(self.newEnv)
            self.dd_dls_open.pop(self.newEnv)
            self.newEnv -= 1
        else:
            pass

        if re.findall(regex_plus, line):
            self.dl_open.append(0)
            self.dd_dls_open.append(0)
            self.newEnv += 1
        else:
            pass

    def remove_sparse_dl(self, line):

        text_cursor: int = 0
        sym_count: int = self.count_symbols_in_string(line, '$')
        sym_overall: int = self.dl_open[self.newEnv] - sym_count
        sym_progress: int = 0
        temp: str = ""
        while text_cursor < len(line) and sym_count>sym_progress:
            if line[text_cursor] == '$':
                if (sym_overall+sym_progress) % 2 == 0:
                    temp += '\('
                else:
                    temp += '\)'
                sym_progress += 1
            else:
                temp += line[text_cursor]
            text_cursor += 1
        temp += line[text_cursor:]
        return temp

    def remove_sparse_ddl(self, line):

        text_cursor: int = 0
        sym_count: int = self.count_symbols_in_string(line, '$$')
        sym_overall: int = self.dd_dls_open[self.newEnv] - sym_count
        sym_progress: int = 0
        temp = ""
        while text_cursor < len(line)-1 and sym_count>sym_progress:
            if line[text_cursor] == '$' and line[(text_cursor+1)] == '$':
                sym_count -= 1
                if (sym_overall + sym_progress) % 2 == 0:
                    temp += '\['
                else:
                    temp += '\]'
                text_cursor += 2
            else:
                temp += line[text_cursor]
                text_cursor += 1
        temp += line[text_cursor:]
        return temp

    def remove_dls(self, array):
        temp = []
        for jj,line in enumerate(array):
            # Remove dollars from text-like environments
            math_no_dls = self.remove_dollars_from_text_env(line)
            # Count the single dollars in the given line
            self.line_dl_open = self.count_symbols_in_string(math_no_dls, '$')
            # Count the double dollars in the given line
            self.line_ddl_open = self.count_symbols_in_string(math_no_dls, '$$')
            # Search for new environments
            self.search_for_environments(math_no_dls)
            # Update the overall count
            if jj >5000and jj < 6000:
                print(line, self.dl_open, self.dd_dls_open, self.newEnv)
            self.dl_open[self.newEnv] += self.line_dl_open
            self.dd_dls_open[self.newEnv] += self.line_ddl_open
            if self.find_open_dls('$$') and self.line_ddl_open % 2 == 0:
                math_no_dls = self.remove_inline_dls(math_no_dls, '$$')
            else:
                math_no_dls = self.remove_sparse_ddl(math_no_dls)
            if self.find_open_dls('$') and self.line_dl_open % 2 == 0:
                math_no_dls = self.remove_inline_dls(math_no_dls, '$')
            else:
                math_no_dls = self.remove_sparse_dl(math_no_dls)



            temp.append(math_no_dls)
        return temp
