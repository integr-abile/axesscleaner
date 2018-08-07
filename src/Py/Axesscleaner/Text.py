import re


class Methods:
    @staticmethod
    def find_axessibility(line):
        if re.search('sepackage( |){axessibility}', line):
            return True
        else:
            return False
    @staticmethod
    def add_axessibility(line):
        return re.sub('\\\\begin{document}', '\\usepackage{axessibility}\n\\\\begin{document}', line)
