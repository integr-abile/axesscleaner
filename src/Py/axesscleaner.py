import argparse
import os.path
import subprocess
from Axesscleaner import Macro, flatex

macro_methods = Macro.Methods()
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

args = parser.parse_args()


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

            with open(args.input, 'r') as i:

                line = macro_methods.strip_comments(i.read())
                macro_methods.gather_macro(line)

            # Reads user-macro file to obtain the user-defined macros. We also remove unwanted comments
            print("gather macros from user defined file")

            if os.path.exists(macro_file):

                with open(macro_file, 'r') as i:

                    line = macro_methods.strip_comments(i.read())
                    macro_methods.gather_macro(line)

            # Remove the macros from the main file and writes the output to a temp file.
            print("remove macros from main file")

            with open(args.input, 'r') as i:

                line = macro_methods.strip_comments(i.read())
                macro_methods.remove_macro(line, temp_file_pre_expansion)

            # Get path of temp file.
            current_path = os.path.split(temp_file_pre_expansion)[0]

            # Include all the external files
            print("include external files in main file")
            final_text_to_expand = macro_methods.strip_comments(''.join(input_latex_methods.expand_file(temp_file_pre_expansion,
                                                                                                        current_path,
                                                                                                        True, False)))

            # Remove temp file
            os.remove(temp_file_pre_expansion)

            # Remove macros from the entire file and put the result to temp file
            print("remove macros from entire file")
            macro_methods.remove_macro(final_text_to_expand, temp_file_pre_expansion)

            # get script folder
            script_path = os.path.abspath(os.path.join(__file__, os.pardir))
            pre_process_path = os.path.join(
                script_path,
                "..",
                "Perl",
                "AxessibilityPreprocess.pl"
            )
            pre_process_compile_path = os.path.join(
                script_path,
                "..",
                "Perl",
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
