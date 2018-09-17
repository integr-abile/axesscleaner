import argparse
import os.path
import subprocess
from Axesscleaner import Macro, flatex, Text

MACRO = Macro.Methods()
TEXT = Text.Methods()
input_latex_methods = flatex.Flatex()

parser = argparse.ArgumentParser(description='This method takes as inputs ')


parser.add_argument('-i',
                    dest='input',
                    help='Input File (Required). It accepts only .tex files')

parser.add_argument('-o',
                    dest='output',
                    default='',
                    help='Output File (optional, default: input file with _clean as suffix)')

parser.add_argument('-p',
                    dest='pdflatex',
                    action='store_const',
                    const=True,
                    default=False,
                    help='If selected, runs pdflatex at the end')

parser.add_argument('-a',
                    dest='addPackage',
                    action='store_const',
                    const=True,
                    default=False,
                    help='If selected, adds axessibility, if not present. If pdflatex is selected, the package is added')


args = parser.parse_args()
args.ospath = os.path.abspath(__file__)


def main():

    # Begin of actual methods. First check if the input is a LaTex file

    if args.input is not None:

        if args.input.endswith('.tex'):

            # Check the number of outputs. If no output is given, create a new one.

            if not args.output:
                a = args.input
                args.output = a.replace('.tex', '_clean.tex')

            # Assign the macro file address and some temporary files.

            folder_path = os.path.abspath(
                os.path.join(os.path.abspath(args.input),
                             os.pardir)
            )
            macro_file = os.path.join(
                folder_path,
                "user_macro.sty"
            )
            temp_file_pre_expansion = os.path.join(
                folder_path,
                "temp_pre.tex"
            )

            # Reads the file preamble to obtain the user-defined macros. We also remove unwanted comments.
            print("gather macros from preamble")

            with input_latex_methods.open_encode_safe(args.input) as i:
                line = MACRO.strip_comments(i.read())
                MACRO.gather_macro(line)

            # Reads user-macro file to obtain the user-defined macros. We also remove unwanted comments
            print("gather macros from user defined file")

            if os.path.exists(macro_file):

                with input_latex_methods.open_encode_safe(macro_file) as i:

                    line = MACRO.strip_comments(i.read())
                    MACRO.gather_macro(line)

            # Remove the macros from the main file and writes the output to a temp file.
            print("remove macros from main file")

            with input_latex_methods.open_encode_safe(args.input) as i:
                line = i.read()
                MACRO.remove_macro(line, temp_file_pre_expansion, False)

            # Get path of temp file.
            current_path = os.path.split(temp_file_pre_expansion)[0]

            # Include all the external files
            print("include external files in main file")
            final_text_to_expand = MACRO.strip_comments(''.join(
                input_latex_methods.expand_file(temp_file_pre_expansion,
                                                current_path,
                                                False,
                                                False)
                )
            )

            # Remove temp file
            os.remove(temp_file_pre_expansion)

            # Remove macros from the entire file and put the result to temp file
            print("remove macros from entire file")
            MACRO.remove_macro(final_text_to_expand,
                               temp_file_pre_expansion,
                               args.addPackage or args.pdflatex)

            # get script folder
            script_path = os.path.abspath(os.path.join(args.ospath, os.pardir))
            perl_path = os.path.join(os.path.dirname(script_path), 'Perl')
            print(perl_path)
            pre_process_path = os.path.join(
                perl_path,
                "AxessibilityPreprocess.pl"
            )
            pre_process_compile_path = os.path.join(
                perl_path,
                "AxessibilityPreprocesspdfLatex.pl"
            )

            # Call perl scripts to clean dollars, underscores.
            # Eventually, it can call also pdflatex, when -p is selected
            if args.pdflatex:
                print("final cleaning file")
                p = subprocess.Popen(
                    [
                        "perl",
                        pre_process_compile_path,
                        "-w",
                        "-o",
                        "-s",
                        temp_file_pre_expansion,
                        args.output
                     ]
                )
            else:
                print("final cleaning file and pdf production")
                p = subprocess.Popen(
                    [
                        "perl",
                        pre_process_path,
                        "-w",
                        "-o",
                        "-s",
                        temp_file_pre_expansion,
                        args.output
                    ]
                )

            # close process.
            p.communicate()

            # remove spurious file
            os.remove(temp_file_pre_expansion)
            os.remove(temp_file_pre_expansion.replace('.tex', '.bak'))
        else:
            print('The file you inserted as input is not a .tex')
    else:
        print('The input is empty')


if __name__ == "__main__":
    main()
