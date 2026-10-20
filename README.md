# Dwed Translator v3.2

A translator for **Dwed** (*Venekmar Dwedmarrum*), the language of the Dwed, a fantasy race of dwarves from [LotC](https://www.lordofthecraft.net/). Dwed was originally documented by chaotikal and has since been extensively expanded and formalized by me, B. Hansen (_Indy / Ferek Frostbeard). It draws on Warhammer Fantasy's Khazalid, Old Norse and Old Germanic roots, and the dictionary now holds over a thousand entries.

The app has two tabs:

- **Dictionary**: word-for-word translation between English and Dwed, with optional runic output.
- **Sentence Builder**: a grammar-aware composer that walks you through tense, subject, verb, object and modifiers, and builds a properly formed Dwed sentence following the *Enecyclopedia of Dwarven Language*.

<img width="500" height="752" alt="Dictionary Tab" src="https://github.com/user-attachments/assets/cbed9f80-ac49-48c8-9097-4495a558724f" /> <img width="500" height="751" alt="Sentence Tab" src="https://github.com/user-attachments/assets/2221376a-9382-45c3-a43d-c9830f108ea1" />




# Start here!

## Requirements

- **Python 3** [(3.8 or newer)](https://www.python.org/downloads/) with **Tkinter**.
That's it. No `pip install` needed; everything else is in Python's standard library.

Tkinter comes bundled with the Python installers from [python.org](https://www.python.org/downloads/) on Windows and macOS. A few setups ship it separately:

- **Debian/Ubuntu Linux:** `sudo apt install python3-tk`
- **Fedora Linux:** `sudo dnf install python3-tkinter`
- **Homebrew Python on macOS:** `brew install python-tk`

Not sure? Run `python -c "import tkinter"`. If it prints nothing, you're good.

## Running it

1. Download the repo (green **Code** button → **Download ZIP**) and unzip it. All the files must stay together in the same folder.
2. Double-click `DwedTranslator_v3_2.py`, or run it from a terminal in that folder:

   ```
   python DwedTranslator_v3_2.py
   ```
<img width="607" height="197" alt="image" src="https://github.com/user-attachments/assets/976bce3f-110f-4f6d-b788-5ab83e620abe" />

No IDE required, though any IDE works fine too (I use [PyCharm](https://www.jetbrains.com/pycharm/), but it's dealer's choice). If something goes wrong at startup, the error appears in a popup instead of the window vanishing.

**Tip (Windows):** rename the file to `DwedTranslator_v3_2.pyw` and it will open without the black console window behind it.

# How to use

## Dictionary tab

- **Source Window** (top): type what you want translated.
- **Source Language / Target Language**: pick the language you typed in and the language you want out. Currently English and Dwed.
- **TRANSLATE**: the result appears in the **Target Window** below and is copied to your clipboard.
- **Dwedic Runes**: outputs the result in Elder Futhark runes instead of Latin script.

Reading the output:

- Words with several meanings come out in brackets, like `[ da , ok ]`. It's up to **YOU** to pick the right one.
- Words that aren't in the dictionary come out as **[x]**.
- This tab substitutes word for word; it doesn't apply grammar. For grammatical sentences, use the Sentence Builder.

## Sentence Builder tab

Pick a sentence type, then fill in the fields. The preview updates as you go.

- **Sentence types:** verbal (action), copular (state of being), imperative (command), yes/no question and wh- question.
- **Tense and aspect:** past, present or future, plus perfect, progressive and negation.
- **Subject:** a pronoun or a proper name.
- **Object:** a noun phrase with optional determiner, possessive, plural and adjectives.
- **Modifiers:** adverbs and prepositional phrases.

The dropdowns are filled from the dictionary, but you can also type a word that isn't listed (a proper noun, say) and it will be used as-is. Hit **Copy** to copy the result, or tick **Dwedic Runes** for runic output.

# The dictionary

`DICTIONARY_dwed.csv` is a plain UTF-8 CSV file, one entry per row:

| Column | What it holds |
|---|---|
| `english` | English word or phrase |
| `dwed` | Dwed translation |
| `class` | Word class (see below) |
| `status` | `auto` (auto-tagged, high confidence), `review` (word class needs checking) or `verified` (checked by a human) |
| `notes` | Optional: etymology, usage notes, anything else |

**Word classes:** `noun`, `verb`, `adjective`, `adverb`, `preposition`, `pronoun`, `conjunction`, `question_word`, `proper_noun`, `numeral`, `interjection`, `particle`, `affix`. The Sentence Builder uses these to fill its dropdowns, so a word tagged with the wrong class shows up in the wrong place.

**Synonyms:** when an English word has more than one Dwed form, each form gets its own row. For example, "the" has one row for `da` and another for `ok`. This is intentional.

**Punctuation rows** (`.`, `,`, `?` and so on) let punctuation pass through the Dictionary tab. Please leave them in.

## Editing it safely

You can edit the CSV in any text editor, in LibreOffice Calc or in Excel. Spreadsheet programs need a little care:

- **Don't just double-click it into Excel.** Excel treats any cell starting with `-` as a formula, so suffixes like `-ing` or `-rumm` turn into `#NAME?`. If you save after that, those entries are destroyed. Instead, use **Data → From Text/CSV**, choose **Transform Data** and set every column to **Text** before loading.
- **LibreOffice Calc** asks how to import the file. Set the columns to **Text**, or uncheck **Evaluate formulas**.
- **Always save as "CSV UTF-8"**, not plain "CSV", or letters like þ, ð and æ get mangled.

GitHub's own file view is a quick, safe way to browse or search the dictionary without downloading anything.

## Adding another language

Every column other than `class`, `status` and `notes` is treated as a language. To add one (Spanish, say), add a `spanish` column and fill in the Spanish words. It appears in the Dictionary tab's language dropdowns automatically.

# File breakdown

1. **`DwedTranslator_v3_2.py`**: the main file. Run this one. It builds the window and both tabs.
2. **`DICTIONARY_dwed.csv`**: the dictionary.
3. **`dwed_lexicon.py`**: loads the dictionary and handles lookups for both tabs.
4. **`dwed_renderer.py`**: the grammar engine. Encodes the Codex's rules as Python functions that turn a sentence description into proper Dwed.
5. **`dwed_runes.py`**: converts Latin script to Dwedic runes.
6. **`legacy_grammar_notes.md`**: old grammar notes from the v2.1 dictionary, kept for history. The Codex supersedes them.

Older versions (v3.1 and earlier, including the Excel dictionary) are on this repo's legacy branch.

# Contributing

New words, corrections and word-class fixes are welcome. Plenty of entries are still marked `review`. Open a pull request with your changes to `DICTIONARY_dwed.csv`, and please follow the column layout above.

Happy translating! :)

—B. Hansen (_Indy) / Ferek Frostbeard

X ᚾᚨᚱᚹᚨᚲ ᛟᛉ ᛞᚨ ᚨᛉᚹᛃᚱᛏᚱᚢᛗᛗ X
