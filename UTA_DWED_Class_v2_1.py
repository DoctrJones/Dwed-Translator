import xlwt, xlrd, openpyxl, re, string, codecs
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


class UTA:
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def loadDictionary(dictionary):
        # Load Dictionary Workbook, Identify B column English
        wb = load_workbook(filename=dictionary)
        ws = wb.active
        columnB = ws['B']
        # Get English List from Excel Dictionary, Convert to lower case
        E_list = [columnB[x].value for x in range(len(columnB))]
        # E_list = [word.lower() for word in E_list]
        return E_list, columnB

    def loadText(text):
        # Get contents of text file to list, lowercase convert. supports UNICODE!
        f = codecs.open(text, encoding="utf-8")
        contents = f.read()
        with open(text, 'r') as f:
            F_list = [word for line in f for word in line.split()]
            F_list = [word.lower() for word in F_list]
        return F_list

    def readText(text):
        # # Gets contents of text file to variable, supports UNICODE!
        f = codecs.open(text, encoding="utf-8")
        contents = f.read()
        return contents

    def loadColAList(file):
        # Get contents of single Excel Column in file, (Column A in this case)
        wb = load_workbook(filename=file)
        ws = wb.active
        columnA = ws['A']
        ColA_list = [columnA[x].value for x in range(len(columnA))]
        Col_List = [*set(ColA_list)]
        Col_List = [item for item in Col_List if item is not None]  # Filter out "None" values
        print(Col_List)
        return Col_List

    def loadExList(file):
        # Get contents of Excel Columns, A being English Language, B being Translated Language
        wb = load_workbook(filename=file)
        ws = wb.active
        columnA = ws['A']
        columnB = ws['B']
        TA_list = [columnA[x].value for x in range(len(columnA))]
        # TA_list = [word.lower() for word in TA_list]
        TB_list = [columnB[x].value for x in range(len(columnB))]
        TB_list = [word.lower() for word in TB_list]
        return TA_list, TB_list, columnA, columnB

    def tempAppendIdent(E_list, TA_list, TB_list):
        T_list = []
        Pos_list = []
        Add_list = []
        Bdd_list = []
        TA_index = 0
        while TA_index < len(TA_list):
            if TA_list[TA_index] in E_list:
                Pos_list.append(E_list.index(TA_list[TA_index]))
                T_list.append(TB_list[TA_index])
                TA_index = TA_index + 1
            else:
                Add_list.append(TA_list[TA_index])
                Bdd_list.append(TB_list[TA_index])
                TA_index = TA_index + 1
        return Pos_list, T_list, Add_list, Bdd_list

    def tempAppendIdent_Translate(R_Column, TInput_list, file):
        # Takes Reference Column and TInput_list, identifies position of TInput_list items
        # within the list structure, filters through punctuation

        # Reload DICTIONARY
        wb = load_workbook(filename=file)
        ws = wb.active

        # Set Reference Column
        column_letter = get_column_letter(R_Column)
        Column = ws[column_letter]
        R_list = [Column[x].value for x in range(len(Column))]
        Pos_list = []
        index = 0
        dummy = "[x]"

        for item in TInput_list:
            # Find all the indexes of the item from TInput_list in the R_Column list (R_list)
            indexes = [index for index, value in enumerate(R_list) if value == item]
            if indexes:
                #If the number of indices is greater than 1, IE: multiple corresponding matches [ruvalk -> flood, river], add a [ and ] to the set
                if len(indexes) > 1:
                    duplicate_list =[]
                    # Place "," between matching indexes
                    for i in indexes:
                        duplicate_list.append(i)
                        duplicate_list.append(",")
                    # Removes last element (will always be a ",")
                    duplicate_list.pop()
                    # Append the duplicate list to the positional list
                    Pos_list.append("[")
                    Pos_list.extend(duplicate_list)
                    Pos_list.append("]")
                # If the number of indices is equal to 1, IE: one corresponding matche [bokk -> rock], append position to list
                if len(indexes) == 1:
                    Pos_list.extend(indexes)
            else:
                # Appends dummy positional value if word not in list
                Pos_list.append(dummy)

        # DEBUGGING PURPOSES, Leaving in just in case ;) print("POS_LIST", Pos_list, "INDEXES", indexes)
        return Pos_list

    def alpnumSort(Tlist):
        # Sorts out non-numerical/letter characters from list, arranges alphabetically
        index = 0
        while index < len(Tlist):
            s = ''.join(filter(str.isalnum, Tlist[index]))
            Tlist[index] = s
            index = index + 1
        Tlist = list(set(Tlist))
        if '' in Tlist:
            Tlist.remove('')
        Tlist.sort()
        return Tlist

    def tempAppend(F_list, E_list):
        # Append new words to Temp Dictionary
        T_list = []
        E_index = len(E_list)
        F_index = 0
        while F_index < len(F_list):
            if F_list[F_index] in E_list:
                F_index = F_index + 1
            else:
                T_list.append(F_list[F_index])
                F_index = F_index + 1
        return T_list

    def translatePositional(Pos_list, Column_L_translation, file):
        # Identifies Word in Translated Column based on Positional Data, replaces Pos_list index with
        # translated word
        index = 0
        wb = load_workbook(filename=file)
        ws = wb.active

        while index < len(Pos_list):
            if str(Pos_list[index]) == '[x]':
                Pos_list[index] = Pos_list[index]
            if str(Pos_list[index]) in string.punctuation:
                Pos_list[index] = Pos_list[index]
            if str(Pos_list[index]) not in string.punctuation and str(Pos_list[index]) != '[x]':
                cell_obj = ws.cell(row=Pos_list[index] + 1, column=int(Column_L_translation))
                Pos_list[index] = cell_obj.value
            if Pos_list[index] == None:
                Pos_list[index] = ('[x]' if Pos_list[index] is None else Pos_list[index])
            index = index + 1
        return Pos_list

    def removeWhiteSpace(List):
        # Input one List, removes all " ", returns modified List
        index = 0
        while index < len(List):
            List[index] = List[index].strip()
            index = index + 1
        return List

    def English2Runic(text):
        # Takes text, changes font to Dwedic (runic)
        futhark_alphabet = {
            'a': 'ᚨ', 'b': 'ᛒ', 'c': 'ᚲ', 'd': 'ᛞ', 'e': 'ᛖ', 'f': 'ᚠ', 'g': 'ᚷ', 'h': 'ᚺ',
            'i': 'ᛁ', 'j': 'ᛃ', 'k': 'ᚲ', 'l': 'ᛚ', 'm': 'ᛗ', 'n': 'ᚾ', 'o': 'ᛟ', 'p': 'ᛈ',
            'q': 'ᚲ', 'r': 'ᚱ', 's': 'ᛊ', 't': 'ᛏ', 'u': 'ᚢ', 'v': 'ᚹ', 'w': 'ᚹ', 'y': 'ᛃ',
            'z': 'ᛉ', ' ': ' ', }
        futhark_text = ''
        for char in text.lower():
            if char in futhark_alphabet:
                futhark_text += futhark_alphabet[char]
            else:
                futhark_text += char
        return futhark_text