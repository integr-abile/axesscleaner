import os
import re


class Flatex:
    @staticmethod
    def is_input(line):
        """
        Determines whether or not a read in line contains an uncommented out
        \input{} statement. Allows only spaces between start of line and
        '\input{}'.
        """
        #tex_input_re = r"""^\s*\\input{[^}]*}""" # input only
        tex_input_re = r"""(^[^\%]*\\input{[^}]*})|(^[^\%]*\\include{[^}]*})"""  # input or include
        return re.search(tex_input_re, line)

    @staticmethod
    def get_input(line):
        """
        Gets the file name from a line containing an input statement.
        """
        tex_input_filename_re = r"""{[^}]*"""
        m = re.search(tex_input_filename_re, line)
        return m.group()[1:]

    @staticmethod
    def combine_path(base_path, relative_ref):
        """
        Combines the base path of the tex document being worked on with the
        relate reference found in that document.
        """
        if (base_path != ""):
            os.chdir(base_path)
        # Handle if .tex is supplied directly with file name or not
        if relative_ref.endswith('.tex'):
            return os.path.join(base_path, relative_ref)
        else:
            return os.path.abspath(relative_ref) + '.tex'

    def expand_file(self, base_file, current_path, include_bbl, noline):
        """
        Recursively-defined function that takes as input a file and returns it
        with all the inputs replaced with the contents of the referenced file.
        """
        output_lines = []
        f = self.open_encode_safe(base_file)
        for line in f:
            if self.is_input(line):
                new_base_file = self.combine_path(current_path, self.get_input(line))
                output_lines += self.expand_file(new_base_file, current_path, include_bbl, noline)
                if noline:
                    pass
                else:
                    output_lines.append('\n')  # add a new line after each file input
            elif include_bbl and line.startswith("\\bibliography") and (not line.startswith("\\bibliographystyle")):
                output_lines += self.bbl_file(base_file)
            else:
                output_lines.append(line)
        f.close()
        return output_lines

    def bbl_file(self, base_file):
        """
        Return content of associated .bbl file
        """
        bbl_path = os.path.abspath(os.path.splitext(base_file)[0]) + '.bbl'
        return self.open_encode_safe(bbl_path).readlines()

    @staticmethod
    def open_encode_safe(file):

        return open(file, 'r')
