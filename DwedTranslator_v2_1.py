from tkinter import *
from tkinter import scrolledtext
import re
from UTA_DWED_Class_v2_1 import UTA
from openpyxl import load_workbook

# This is the Dwed Translator v2.1, updated as of 20240503. The purpose of this program is to translate between English
# and Dwed, a fictional language that was extensively worked upon by me, Benjamin Hansen AKA Doctor Jones AKA indy_
#
# This program will open a Tkinter GUI with an input window, and two dropdowns: source and target languages. Select
# the source language (the language used in the entry window) and the target language, enter your desired text,
# and hit TRANSLATE. The translated text will be displayed below in a separate window, and copied
# to your machine's clipboard.
#
# I am by NO means a professional, this has been a work-in-progress since December of 2020. I make no claim to the
# cleanliness of this code, it at times confuses the fuck out of me. Regardless, it does what I want it to, so I
# don't complain!
#
# Happy translating! :)

file = "DICTIONARY_dwed.xlsx"
Source_List = (UTA.loadColAList(file))

#-----TEXT TRANSLATOR CODE-----
def TextTranslator_func():
    # Load DICTIONARY Workbook, Identify A Column English V
    file = "DICTIONARY_dwed.xlsx"
    wb = load_workbook(filename=file)
    ws = wb.active
    E_list, columnA = UTA.loadDictionary(file)
    # Establish DICTIONARY register
    register = ws['A']
    register = [register[x].value for x in range(len(register))]
    register = [i for i in register if i]
    # Create list from text input
    # Get contents of text file to list, lowercase convert
    text = (entry_text.get('1.0',END))
    contents = text
    contents = contents.lower()
    # Separate punctuation, but retain in Input_list
    Input_list = re.findall(r"\w+|[^\w\s]", contents)
    # Prompt what language to translate to, store Column Identifiers
    L_text = S_clicked.get()
    if L_text in register:
        Column_L_text = register.index(L_text) + 2
    L_translation = T_clicked.get()
    if L_translation in register:
        Column_L_translation = register.index(L_translation) + 2
    if L_translation not in register:
        return("Language not in DICTIONARY!")
        quit()
    # Identify location of word in Reference Column, Export position of words to positional list
    Positional_list = UTA.tempAppendIdent_Translate(Column_L_text, Input_list, file)
    # Replace Numbers in Positional List with translated equivalents
    Translated_list = UTA.translatePositional(Positional_list, Column_L_translation, file)
    # Compend Translated_list to concatted string
    Comp_Trans_list = ' '.join(Translated_list)
    window.clipboard_clear()
    window.clipboard_append(Comp_Trans_list)
    window.update()
    return Comp_Trans_list

def TextTransDisplay():
    # This function updates the main window to display the translated text
    # Translates the entry text to desired language
    Trans_Text = TextTranslator_func()
    # Checks to see if "Dwedic Runes" button is true. If so, changes font from English script to Dwedic runes
    dwed_state = dwed_var.get()
    if dwed_state == 1:
        Trans_Text = UTA.English2Runic(Trans_Text)
    # Updates main window to display translated text
    Trans_Text_Display = Text(window, width=40, height=10, wrap=WORD, bg="white", font="none 12 bold")
    Trans_Text_Display.grid(row=7, column=0, sticky=N)
    Label(window, text="copied to clipboard", bg="black", fg="white", font="none 12 bold") .grid(
        row=8, column=0, sticky=N)
    Trans_Text_Display.insert(END,Trans_Text)


#------GUI SECTION-----

#Initialization
window = Tk()
window.title("Dwed Translator Application V2.1 (20240503)")
window.configure(background="black")
window.geometry("370x500")
window.resizable(1,1)
S_clicked = StringVar(window)
T_clicked = StringVar(window)


#-----LABELS-----
Label(window, text="Common <-> ᛞᚹᛖᛞ Translator", bg="black", fg="grey", font="none 12 bold") .grid(row=1,column=0, sticky=N)
Label(window, text="Source Language", bg="black", fg="grey", font="none 12 bold") .grid(row=4,column=0, sticky=W, pady=2)
Label(window, text="Target Language", bg="black", fg="grey", font="none 12 bold") .grid(row=5,column=0, sticky=W, pady=2)

#-----ENTRIES-----
entry_text = scrolledtext.ScrolledText(window, width=40, height=10, bg="white")
entry_text.grid(row=3, column=0,sticky=N)
# Source_language = Entry(window, width=15, bg="grey")
Source_Drop = OptionMenu(window, S_clicked, *Source_List)
Source_Drop.config(width=15)  # Set the width of the Source OptionMenu
Source_Drop.grid(row=4, column=0, sticky=E)
# Translated_language = Entry(window, width=15, bg="grey")
Translated_Drop = OptionMenu(window, T_clicked, *Source_List)
Translated_Drop.config(width=15)  # Set the width of the Translated OptionMenu
Translated_Drop.grid(row=5, column=0, sticky=E)

#-----BUTTONS-----
t_button = Button(window, text="          ||TRANSLATE||          ", command=TextTransDisplay) .grid(row=6, column=0, sticky=W)
dwed_var = IntVar() #1 for True, 0 for False
dwedic_script_button = Checkbutton(window, text="     Dwedic Runes      ", variable=dwed_var) .grid(row=6, column=0, sticky=E)

# Code for maintaining window loop
window.mainloop()