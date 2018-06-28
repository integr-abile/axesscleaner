# AxessCleaner


This python module cleans a LaTex file in order to use the ``axessibility.sty``` package safely. It handles the following:
* User defined macro e.g ```\def, \newcommand```, with and without inputs. 
* Dollars-defined math environments, e.g ``` $$\sqrt{4}$$``` 
* Underscore
* Include external files with ```\include, \input```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for usage, development and testing.

### Prerequisites

In order to use ```axesscleaner.py``` you need

* python  Python 2 >=2.7.9 or Python 3 >=3.4  (https://www.python.org)
* pip (https://pip.pypa.io/en/stable/installing/)
* For the pdflatex version, you need a working tex distribution.
    * TexLive 
        * Mac Osx (http://www.tug.org/mactex/)
        * Windows, Ubuntu (https://www.tug.org/texlive/)
    * MikTex (https://miktex.org)
    

### Installing

Download the folder on your local computer and unzip the content. 

#### Linux/ Mac Osx

Open the terminal. 
Inside the terminal, go to the directory where the folder is stored using 


```cd <address of your folder>```

For example, if your folder **Axesscleaner** is inside **Documents**, you can do 

```cd ~/Documents/Axesscleaner```  

Then run

```pip upgrade```

to update the version of pip. The next command installs all the dependencies

```pip install -r requirements.txt```


Optionally, you can set up a virtualenv and do the same steps inside it (https://docs.python.org/3/library/venv.html).

## Usage

Now, you are ready tu use our module from the command line. Let's look into the input/output structure.

By executing ```python axesscleaner.py -h``` you get the following output

```
optional arguments:
  -h, --help  show this help message and exit
  -i INPUT    Input File (Required). It accepts only .tex files
  -o OUTPUT   Output File (optional, default: input file with _clean as
              suffix)
  -p          If selected, runs pdflatex at the end

```

Hence, in order to clean a file, execute:

```
axesscleaner.py -i <input file>.tex 

```
It will generate ```<input file>_clean.tex ``` in the same folder as the input file. With the option ```-p```, i.e. 

```
axesscleaner.py -i <input file>.tex -p 

```
It will also generate the log files and the ```input file>_clean.pdf```

To specify an output, you can execute:

```
axesscleaner.py -i <input file>.tex -o <output file>.tex

```
with or without ```-p```.

##Main Contributors

* Dragan Ahmetovic
* Tiziana Armano
* Cristian Bernareggi
* Michele Berra
* Sandro Coriasco
* Nadir Murru

See also the website of the project (www.integr-abile.unito.it) for the full list of contributors and testers.
 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [ProgressBar](https://github.com/bozoh/console_progressbar)
* Perl scripts inspired by:
* [Flatex](https://github.com/johnjosephhorton/flatex)
* [StripComments](https://gist.github.com/amerberg/a273ca1e579ab573b499)
