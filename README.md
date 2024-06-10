# Start here!
These are the base files necessary for running the Dwed Translator Application, not including the required Python libraries required for running. This distribution is designed to be run from a Python IDE of your choosing.

### **How to use:**

These files must all reside in the same directory in order to be used.

![image](https://github.com/DoctrJones/Dwed-Translator/assets/161623020/fa82c9b5-3aa5-4b51-a25d-1b5c81736f6f)

- The first entry window is the Source Window, this is where you would enter what you want translated. Currently, only supports English and Dwed entries

- The second entry window, which appears below, is the result of translation (AKA Target Window). The contents of this window are copied to your machine's clipboard for convenience. Note, words with multiple meanings will be encased in ' [ ] ', it's up to _**YOU**_ to determine which word to use. Additionally, any word entered in the Source Window that does NOT have a translation in the dictionary will result in an **[x]** in the Target Window.

- Source Language is the language used in the Source Window

- Target Language is the language output in the Target Window

- The Dwedic Runes checkbox will change the output of the Target Window to be in Elder Futharc runes, as opposed to Latin script.

# Library Installs
To install the libraries needed for running this program, please run these pip commands:

(Note, this can be done either in your IDE's console, or from your command terminal [if you have it set up that way, idk you're probably a smart cookie and can figure it out])

`pip install openpyxl`

`pip install tkinter`


# File Breakdown

1) DICTIONARY_dwed.xlsx : This is the raw "dictionary", in .xlsx format.
  - Column A has two languages, english and dwed. Each row in this column corresponds to the language in the proceeding columns. Example: A1 (English) = Column B (English), A2 (Dwed) = Column C (Dwed), etc. If you wish to edit this file for a different language (Example, add Spanish <-> Dwed functionality), you'd add "spanish" to A3, then the corresponding Spanish words to Column D.

2) DwedTranslator_v2_1.py : This is the main file that runs/handles the GUI

3) UTA_DWED_Class_v2_1.py : This is the class file. This is where the magic happens, everything under the hood happens here.
