import argparse
import os.path
import subprocess
from Axesscleaner import Macro, flatex

axmacro = Macro.Macro()
axflatex = flatex.Flatex()

parser = argparse.ArgumentParser(description='This method takes as inputs ')


parser.add_argument('-i', dest='input',
                    help='Input File (Required). It accepts only .tex files')

parser.add_argument('-o', dest='output', default='',
                    help='Output File (optional, default: input file with _clean as suffix)')

parser.add_argument('-p', dest='pdflatex', action='store_const',
                    const=True, default=False,
                    help='If selected, runs pdflatex at the end')

args = parser.parse_args()


def main():
    # Begin of actual methods. First check if the input is a LaTex file
    MACRO_LIST = []
    if args.input is not None:
        if args.input.endswith('.tex'):
            # Check the number of outputs. If no output is given, create a new one.
            if not args.output:
                a = args.input
                args.output = a.replace('.tex', '_clean.tex')
            # Assign the macro file address and some temporary files.
            FOLDER_PATH = os.path.abspath(os.path.join(os.path.abspath(args.input), os.pardir))
            MACRO_FILE = os.path.join(FOLDER_PATH, "user_macro.sty")
            TEMP_FILE_PRE_EXPANSION = os.path.join(FOLDER_PATH, "temp_pre.tex")

            # Reads the file preamble to obtain the user-defined macros. We also remove unwanted comments.
            print("gather macros from preamble")
            with open(args.input, 'r') as i:
                line = axmacro.strip_comments(i.read())
                MACRO_LIST.extend(axmacro.gather_macro(line))

            # Reads user-macro file to obtain the user-defined macros. We also remove unwanted comments
            print("gather macros from user defined file")
            if os.path.exists(MACRO_FILE):
                with open(MACRO_FILE, 'r') as i:
                    line = axmacro.strip_comments(i.read())
                    MACRO_LIST.extend(axmacro.gather_macro(line))

            # Remove the macros from the main file and writes the output to a temp file.
            print("remove macros from main file")
            with open(args.input, 'r') as i:
                line = axmacro.strip_comments(i.read())
                axmacro.remove_macro(line, TEMP_FILE_PRE_EXPANSION, MACRO_LIST)

            # Get path of temp file.
            current_path = os.path.split(TEMP_FILE_PRE_EXPANSION)[0]

            # Include all the external files
            print("include external files in main file")
            final_text_to_expand = axmacro.strip_comments(''.join(axflatex.expand_file(TEMP_FILE_PRE_EXPANSION, current_path, True, False)))

            # Remove temp file
            os.remove(TEMP_FILE_PRE_EXPANSION)

            # Remove macros from the entire file and put the result to temp file
            print("remove macros from entire file")
            axmacro.remove_macro(final_text_to_expand, TEMP_FILE_PRE_EXPANSION, MACRO_LIST)

            # get script folder
            script_path = os.path.abspath(os.path.join(__file__, os.pardir))
            preprocess_path = os.path.join(script_path, "..", "Perl", "AxessibilityPreprocess.pl")
            preprocess_compile_path = os.path.join(script_path, "..", "Perl", "AxessibilityPreprocesspdfLatex.pl")


            # Call perl scripts to clean dollars, underscores.
            # Eventually, it can call also pdflatex, when -p is selected
            if args.pdflatex:
                print("final cleaning file")
                p = subprocess.Popen(
                    ["perl", preprocess_compile_path, "-w", "-o", "-s", TEMP_FILE_PRE_EXPANSION, args.output])
            else:
                print("final cleaning file and pdf production")
                p = subprocess.Popen(
                    ["perl", preprocess_path, "-w", "-o", "-s", TEMP_FILE_PRE_EXPANSION, args.output])

            # close process.
            p.communicate()

            # remove spurious file
            os.remove(TEMP_FILE_PRE_EXPANSION)
            os.remove(TEMP_FILE_PRE_EXPANSION.replace('.tex', '.bak'))
        else:
            print('The file you inserted as input is not a .tex')
    else:
        print('The input is empty')


if __name__ == "__main__":
    main()
