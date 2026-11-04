"""
Dwed Translator v3.2 — with functional Sentence Builder tab.

-Adds a grammar-aware sentence composer that walks the user through the
grammatical decisions in the Codex of Dwarven Grammar (4th Edition) and
produces properly-formed Dwed sentences via the dwed_renderer module.
-Dictionary now stored as a plain UTF-8 CSV (DICTIONARY_dwed.csv); no Excel
or third-party libraries required.
-Adds a Runes tab that transliterates typed text into Dwedic runes as you type.

-----------------------------------------------------------------------------------------------------------------------
=Header Info=
This is the Dwed Translator v3.2, updated as of 20261020.
The purpose of this program is to translate between English and Dwed,
a fictional language that was originally documented by chaotikal, then
extensively worked upon by me, B.Hansen AKA Doctor Jones AKA _Indy

This program will open a Tkinter GUI with an input window, and two dropdowns: source and target languages.
Select the source language (the language used in the entry window)
and the target language (Dwed or English, the only ones available in this specific version of the program),
enter your desired text, and hit TRANSLATE. The translated textwill be displayed below in a separate window,
and copied to your machine's clipboard.

Happy translating! :)

—B.Hansen (_Indy) / Ferek Frostbeard
X ᚾᚨᚱᚹᚨᚲ ᛟᛉ ᛞᚨ ᚨᛉᚹᛃᚱᛏᚱᚢᛗᛗ X
-----------------------------------------------------------------------------------------------------------------------
=Maintenance Notes=
If the user wishes to include more words/expand language and maintain usability of this translator, all you have to do
is add rows to DICTIONARY_dwed.csv (columns: english, dwed, class, status, notes). Any spreadsheet program or text
editor works; if you use Excel, save as "CSV UTF-8" so the Norse letters and runes survive.
To add another language, add a column to the CSV; it appears in the Dictionary tab's dropdowns automatically.
"""

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import re
from pathlib import Path

from dwed_renderer import render
from dwed_lexicon import DwedLexicon
from dwed_runes import english_to_runic


# Resolve next to this script, so it works no matter which folder Python starts in
# (double-click, "Open with", a terminal elsewhere, or an IDE).
DICTIONARY_FILE = Path(__file__).resolve().parent / "DICTIONARY_dwed_3511.csv"


# =============================================================================
# THEME — shared black theme setup
# =============================================================================

def apply_theme(root):
    """Configure a consistent black theme across ttk widgets."""
    root.configure(background="black")
    style = ttk.Style(root)
    style.theme_use("default")

    style.configure("TFrame", background="black")
    style.configure("TLabelframe", background="black", foreground="grey",
                    borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background="black", foreground="grey",
                    font=("none", 10, "bold"))
    style.configure("TNotebook", background="black", borderwidth=0)
    style.configure("TNotebook.Tab", background="#222", foreground="grey",
                    padding=[12, 5])
    style.map("TNotebook.Tab",
              background=[("selected", "black")],
              foreground=[("selected", "white")])
    style.configure("TLabel", background="black", foreground="grey")
    style.configure("TButton", background="#222", foreground="black")
    style.configure("TCheckbutton", background="black", foreground="grey")
    style.map("TCheckbutton", background=[("active", "black")])
    style.configure("TRadiobutton", background="black", foreground="grey")
    style.map("TRadiobutton", background=[("active", "black")])
    style.configure("TCombobox", fieldbackground="white", background="#222")


# =============================================================================
# DICTIONARY TAB
# =============================================================================

class DictionaryTab(ttk.Frame):
    def __init__(self, parent, lexicon):
        super().__init__(parent, padding=10)
        self.lex = lexicon
        self.source_list = self.lex.languages()
        self.s_clicked = StringVar(self)
        self.t_clicked = StringVar(self)
        self.dwed_var = IntVar()
        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text="Common <-> ᛞᚹᛖᛞ Translator",
                  font="none 12 bold").grid(row=0, column=0, columnspan=2,
                                            pady=(0, 8), sticky=N)
        self.entry_text = scrolledtext.ScrolledText(
            self, width=40, height=10, bg="white")
        self.entry_text.grid(row=1, column=0, columnspan=2, sticky=N)

        ttk.Label(self, text="Source Language",
                  font="none 10 bold").grid(row=2, column=0, sticky=W, pady=(6, 2))
        source_drop = ttk.OptionMenu(self, self.s_clicked,
                                     self.source_list[0], *self.source_list)
        source_drop.config(width=15)
        source_drop.grid(row=2, column=1, sticky=E)

        ttk.Label(self, text="Target Language",
                  font="none 10 bold").grid(row=3, column=0, sticky=W, pady=2)
        target_drop = ttk.OptionMenu(self, self.t_clicked,
                                     self.source_list[0], *self.source_list)
        target_drop.config(width=15)
        target_drop.grid(row=3, column=1, sticky=E)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=8, sticky=EW)
        ttk.Button(button_frame, text="  ||TRANSLATE||  ",
                   command=self._on_translate).pack(side=LEFT)
        ttk.Checkbutton(button_frame, text="Dwedic Runes",
                        variable=self.dwed_var).pack(side=RIGHT)

        self.output_text = Text(self, width=40, height=10, wrap=WORD,
                                bg="white", font="none 12 bold")
        self.output_text.grid(row=5, column=0, columnspan=2, sticky=N, pady=(4, 2))
        ttk.Label(self, text="copied to clipboard",
                  font="none 10 bold").grid(row=6, column=0, columnspan=2, sticky=N)

    def _translate(self):
        text = self.entry_text.get('1.0', END).lower()
        # input_list = re.findall(r"\w+|[^\w\s]", text) OLD, original code
        input_list = re.findall(r"[\w\-']+|[^\w\s\-']", text)

        source_label = self.s_clicked.get()
        target_label = self.t_clicked.get()
        if source_label not in self.source_list or target_label not in self.source_list:
            return "[Language not in DICTIONARY!]"

        translated = self.lex.translate_tokens(input_list, source_label, target_label)
        return ' '.join(translated)

    def _on_translate(self):
        result = self._translate()
        if self.dwed_var.get() == 1:
            result = english_to_runic(result)
        self.output_text.delete('1.0', END)
        self.output_text.insert(END, result)
        self.clipboard_clear()
        self.clipboard_append(result)
        self.update()


# =============================================================================
# NOUN PHRASE BUILDER — reusable inline component
# =============================================================================

class NounPhraseBuilder(ttk.LabelFrame):
    """Compact inline builder for a Dwed noun phrase.

    Emits a noun-phrase dict via .to_dict() that the renderer can consume.
    All fields optional except the noun itself.
    """

    DETERMINERS = ["(none)", "the", "this", "that"]
    POSS_TYPES = ["(none)", "my", "our", "your", "his", "her", "their", "proper name..."]
    ADJ_SUFFIXES = ["-os", "-mos", "-rum"]

    def __init__(self, parent, lexicon, title="Noun Phrase", on_change=None):
        super().__init__(parent, text=title, padding=6)
        self.lex = lexicon
        self.on_change = on_change or (lambda: None)

        # Vars
        self.det_var = StringVar(value="(none)")
        self.poss_type_var = StringVar(value="(none)")
        self.poss_proper_var = StringVar(value="")
        self.noun_var = StringVar(value="")
        self.plural_var = IntVar(value=0)
        self.adj_var = StringVar(value="")
        self.adj_suffix_var = StringVar(value="-os")

        self.adjectives = []  # list of English adjective labels currently added

        self._build_widgets()
        self._wire_change_events()

    def _build_widgets(self):
        # Row 0: Determiner
        ttk.Label(self, text="Determiner:").grid(row=0, column=0, sticky=W, padx=2)
        det_cb = ttk.Combobox(self, textvariable=self.det_var,
                              values=self.DETERMINERS, width=12, state="readonly")
        det_cb.grid(row=0, column=1, sticky=W, padx=2, pady=1)

        # Row 1: Possessive
        ttk.Label(self, text="Possessive:").grid(row=1, column=0, sticky=W, padx=2)
        poss_cb = ttk.Combobox(self, textvariable=self.poss_type_var,
                               values=self.POSS_TYPES, width=15, state="readonly")
        poss_cb.grid(row=1, column=1, sticky=W, padx=2, pady=1)
        self.poss_proper_entry = ttk.Entry(self, textvariable=self.poss_proper_var, width=15)
        self.poss_proper_entry.grid(row=1, column=2, sticky=W, padx=2, pady=1)
        self.poss_proper_entry.grid_remove()  # hidden until "proper name..." picked

        # Row 2: Noun (required)
        ttk.Label(self, text="Noun *:").grid(row=2, column=0, sticky=W, padx=2)
        noun_cb = ttk.Combobox(self, textvariable=self.noun_var,
                               values=self.lex.english_labels_of_class("noun"),
                               width=25)
        noun_cb.grid(row=2, column=1, columnspan=2, sticky=W, padx=2, pady=1)

        # Row 3: Plural checkbox
        ttk.Checkbutton(self, text="Plural (add -mar)", variable=self.plural_var
                        ).grid(row=3, column=1, sticky=W, padx=2, pady=1)

        # Row 4: Adjectives
        ttk.Label(self, text="Adjective:").grid(row=4, column=0, sticky=W, padx=2)
        adj_cb = ttk.Combobox(self, textvariable=self.adj_var,
                              values=self.lex.english_labels_of_class("adjective"),
                              width=20)
        adj_cb.grid(row=4, column=1, sticky=W, padx=2, pady=1)
        ttk.Button(self, text="+ add", command=self._add_adjective, width=6
                   ).grid(row=4, column=2, sticky=W, padx=2, pady=1)

        # Row 5: Adjective list display + suffix picker
        self.adj_list_label = ttk.Label(self, text="", foreground="lightgreen")
        self.adj_list_label.grid(row=5, column=1, columnspan=2, sticky=W, padx=2, pady=1)

        ttk.Label(self, text="Adj. suffix:").grid(row=6, column=0, sticky=W, padx=2)
        adj_suf_cb = ttk.Combobox(self, textvariable=self.adj_suffix_var,
                                  values=self.ADJ_SUFFIXES, width=6, state="readonly")
        adj_suf_cb.grid(row=6, column=1, sticky=W, padx=2, pady=1)

    def _wire_change_events(self):
        for var in (self.det_var, self.poss_type_var, self.poss_proper_var,
                    self.noun_var, self.plural_var, self.adj_suffix_var):
            var.trace_add("write", lambda *a: self._on_field_change())

    def _on_field_change(self):
        # Show/hide proper-name entry
        if self.poss_type_var.get() == "proper name...":
            self.poss_proper_entry.grid()
        else:
            self.poss_proper_entry.grid_remove()
        self.on_change()

    def _add_adjective(self):
        val = self.adj_var.get().strip()
        if val and val not in self.adjectives:
            self.adjectives.append(val)
            self.adj_var.set("")
            self._refresh_adj_list()
            self.on_change()

    def _refresh_adj_list(self):
        if self.adjectives:
            text = "adjectives: " + ", ".join(self.adjectives) + "  (click to clear)"
        else:
            text = ""
        self.adj_list_label.config(text=text)
        self.adj_list_label.bind("<Button-1>", lambda e: self._clear_adjectives())

    def _clear_adjectives(self):
        self.adjectives = []
        self._refresh_adj_list()
        self.on_change()

    def to_dict(self):
        """Emit the NP as a dict for the renderer. Returns None if noun missing."""
        english_noun = self.noun_var.get().strip()
        if not english_noun:
            return None

        # Look up in dictionary; if not found, fall back to the typed value
        # (user may be typing a Dwed word directly, or a proper noun, or a
        # word not yet in the dictionary)
        dwed_noun = self.lex.translate_one(english_noun) or english_noun

        np = {"noun": dwed_noun}

        det = self.det_var.get()
        if det != "(none)":
            np["determiner"] = det

        poss_type = self.poss_type_var.get()
        if poss_type not in ("(none)",):
            if poss_type == "proper name...":
                name = self.poss_proper_var.get().strip()
                if name:
                    np["possessive"] = {
                        "possessor": {"type": "proper", "value": name},
                        "style": "suffix",  # proper names always use suffix -edos
                    }
            else:
                np["possessive"] = {
                    "possessor": {"type": "pronoun", "value": poss_type},
                    "style": "prefix",  # pronouns default to prefix; user can override in advanced
                }

        if self.plural_var.get():
            np["plural"] = True

        if self.adjectives:
            adj_roots = [self.lex.translate_one(adj) or adj for adj in self.adjectives]
            np["adjectives"] = adj_roots
            suffix_choice = self.adj_suffix_var.get().lstrip("-")
            np["adj_suffix"] = suffix_choice

        return np


# =============================================================================
# OBLIQUE / MODIFIER LIST — reusable component for adverbs and prep phrases
# =============================================================================

class ObliqueList(ttk.LabelFrame):
    """Manages a list of adverbial modifiers on a sentence.

    Each modifier is either:
      - an adverb (free text or dictionary lookup — e.g. "khrum lakh", "vlokon'a")
      - a prepositional phrase (preposition + noun, optional determiner)

    Emits a list-of-dicts via .to_list() for the renderer's `obliques` slot.
    Live-updates via on_change callback whenever a field changes.
    """

    def __init__(self, parent, lexicon, on_change=None):
        super().__init__(parent, text="Modifiers (adverbials)", padding=6)
        self.lex = lexicon
        self.on_change = on_change or (lambda: None)

        self._prepositions = self.lex.english_labels_of_class("preposition")
        self._adverbs = self.lex.english_labels_of_class("adverb")

        self.rows = []  # list of dicts describing each row's widgets/state

        self._build_widgets()

    def _build_widgets(self):
        # Header row: add buttons
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 4))
        ttk.Button(header, text="+ Adverb", command=self._add_adverb_row,
                   width=10).pack(side=LEFT, padx=2)
        ttk.Button(header, text="+ Prep. Phrase", command=self._add_pp_row,
                   width=14).pack(side=LEFT, padx=2)

        # Container for rows
        self.rows_container = ttk.Frame(self)
        self.rows_container.pack(fill=X)

    def _add_adverb_row(self):
        """Add a new adverb modifier row."""
        row_frame = ttk.Frame(self.rows_container)
        row_frame.pack(fill=X, pady=1)

        ttk.Label(row_frame, text="Adv:", width=6).pack(side=LEFT)
        value_var = StringVar()
        value_var.trace_add("write", lambda *a: self.on_change())

        cb = ttk.Combobox(row_frame, textvariable=value_var,
                          values=self._adverbs, width=25)
        cb.pack(side=LEFT, padx=2, fill=X, expand=True)

        row_info = {"type": "adverb", "frame": row_frame, "value_var": value_var}

        del_btn = ttk.Button(row_frame, text="x", width=2,
                             command=lambda: self._remove_row(row_info))
        del_btn.pack(side=RIGHT, padx=2)

        self.rows.append(row_info)
        self.on_change()

    def _add_pp_row(self):
        """Add a new prepositional-phrase modifier row."""
        row_frame = ttk.Frame(self.rows_container)
        row_frame.pack(fill=X, pady=1)

        ttk.Label(row_frame, text="Prep:", width=6).pack(side=LEFT)

        prep_var = StringVar()
        det_var = StringVar(value="(none)")
        noun_var = StringVar()

        for v in (prep_var, det_var, noun_var):
            v.trace_add("write", lambda *a: self.on_change())

        prep_cb = ttk.Combobox(row_frame, textvariable=prep_var,
                               values=self._prepositions, width=12)
        prep_cb.pack(side=LEFT, padx=2)

        det_cb = ttk.Combobox(row_frame, textvariable=det_var,
                              values=["(none)", "the", "this", "that"],
                              width=8, state="readonly")
        det_cb.pack(side=LEFT, padx=2)

        noun_cb = ttk.Combobox(row_frame, textvariable=noun_var,
                               values=self.lex.english_labels_of_class("noun"),
                               width=18)
        noun_cb.pack(side=LEFT, padx=2, fill=X, expand=True)

        row_info = {
            "type": "prep",
            "frame": row_frame,
            "prep_var": prep_var,
            "det_var": det_var,
            "noun_var": noun_var,
        }

        del_btn = ttk.Button(row_frame, text="x", width=2,
                             command=lambda: self._remove_row(row_info))
        del_btn.pack(side=RIGHT, padx=2)

        self.rows.append(row_info)
        self.on_change()

    def _remove_row(self, row_info):
        row_info["frame"].destroy()
        self.rows.remove(row_info)
        self.on_change()

    def _translate_adverb(self, english):
        """Look up an adverb, with several fallback strategies.

        Handles:
          1. Direct dictionary lookup ("suddenly" -> "vlokon'a")
          2. Compound word-by-word ("all day" -> "khrum lakh")
          3. English -ly derivation via Codex rule ("quickly" -> look up "quick"
             as adjective, then append 'a suffix -> "vlokon'a")
          4. Falls back to typed value if all lookups fail
        """
        english = english.strip()
        if not english:
            return ""

        # 1. Try whole-phrase lookup first
        whole = self.lex.translate_one(english)
        if whole:
            return whole

        # 2. English -ly derivation via Codex adverb-formation rule
        # If input ends in -ly and the stem exists as an adjective,
        # derive the Dwed adverb form: <adjective>'a
        if english.endswith("ly") and len(english) > 3:
            stem = english[:-2]  # "quickly" -> "quick"
            # Handle "-ily" -> "-y" (happily -> happy)
            if stem.endswith("i"):
                stem = stem[:-1] + "y"
            stem_dwed = self.lex.translate_one(stem)
            if stem_dwed:
                return f"{stem_dwed}'a"

        # 3. Fall back: translate each word, join with spaces
        words = english.split()
        if len(words) > 1:
            translated = []
            for w in words:
                t = self.lex.translate_one(w)
                translated.append(t if t else w)
            return " ".join(translated)

        # 4. Nothing worked — use as-is
        return english

    def to_list(self):
        """Emit the current modifiers as a list of dicts for the renderer."""
        result = []

        for row in self.rows:
            if row["type"] == "adverb":
                english = row["value_var"].get().strip()
                if not english:
                    continue
                dwed = self._translate_adverb(english)
                result.append({"type": "adverb", "value": dwed})

            elif row["type"] == "prep":
                prep_english = row["prep_var"].get().strip()
                noun_english = row["noun_var"].get().strip()
                if not prep_english or not noun_english:
                    continue
                prep_dwed = self.lex.translate_one(prep_english) or prep_english
                noun_dwed = self.lex.translate_one(noun_english) or noun_english

                pp = {
                    "type": "prep",
                    "preposition": prep_dwed,
                    "object": {"noun": noun_dwed},
                }
                det = row["det_var"].get()
                if det != "(none)":
                    pp["object"]["determiner"] = det

                result.append(pp)

        return result


# =============================================================================
# SENTENCE BUILDER TAB — main structure
# =============================================================================

class SentenceBuilderTab(ttk.Frame):
    """Grammar-aware sentence composer.

    Layout:
        [Sentence type selector]  (top)
        [Dynamic form area]       (middle — changes based on type)
        [Live preview + copy]     (bottom)
    """

    SENTENCE_TYPES = [
        ("Verbal (action)",       "verbal"),
        ("Copular (state of being)", "copular"),
        ("Imperative (command)",  "imperative"),
        ("Question — yes/no",     "question_yn"),
        ("Question — wh-",        "question_wh"),
    ]

    TENSES = [("Past", "past"), ("Present", "present"), ("Future", "future")]
    PRONOUNS = ["I", "we", "you", "he", "she", "it", "they"]
    QUESTION_WORDS = ["what", "where", "why", "who", "which", "how"]
    COPULAS = ["yol-mer", "va-mer", "moredos"]

    def __init__(self, parent, lexicon):
        super().__init__(parent, padding=8)
        self.lex = lexicon

        # State
        self.stype_var = StringVar(value="verbal")
        self.runic_var = IntVar(value=0)

        # Verbal/question fields
        self.tense_var = StringVar(value="present")
        self.perfect_var = IntVar(value=0)
        self.progressive_var = IntVar(value=0)
        self.negation_var = IntVar(value=0)
        self.subject_type_var = StringVar(value="pronoun")  # or "proper" or "noun_phrase"
        self.subject_pronoun_var = StringVar(value="I")
        self.subject_proper_var = StringVar(value="")
        self.verb_var = StringVar(value="")
        self.qword_var = StringVar(value="what")

        # Copular fields
        self.cop_subj_pronoun_var = StringVar(value="he")
        self.cop_copula_var = StringVar(value="yol-mer")

        # Imperative fields
        self.imp_tense_var = StringVar(value="present")
        self.imp_verb_var = StringVar(value="")
        self.imp_negation_var = IntVar(value=0)

        # Dynamic child widgets (created/destroyed based on type)
        self._dynamic_widgets = []
        self.object_np = None
        self.oblique_list = None
        self.cop_pred_type_var = StringVar(value="adjective")
        self.cop_pred_adj_var = StringVar(value="")

        # Preview area
        self.preview_text = None

        self._build_widgets()
        self._render_form_for_type()
        self._wire_state_changes()

    # ---- Layout ----

    def _build_widgets(self):
        # Top: sentence type selector
        top = ttk.Frame(self)
        top.pack(fill=X, pady=(0, 6))
        ttk.Label(top, text="Sentence Type:",
                  font="none 11 bold").pack(side=LEFT, padx=(0, 6))
        type_cb = ttk.Combobox(top, textvariable=self.stype_var,
                               values=[k for k, _ in self.SENTENCE_TYPES],
                               state="readonly", width=30)
        type_cb.pack(side=LEFT)
        type_cb.set(self.SENTENCE_TYPES[0][0])
        type_cb.bind("<<ComboboxSelected>>", lambda e: self._on_type_change())

        # Bottom: preview + controls
        bottom = ttk.LabelFrame(self, text="Preview", padding=6)
        bottom.pack(side=BOTTOM, fill=X, pady=(6, 0))

        self.preview_text = Text(bottom, height=3, wrap=WORD, bg="white",
                                 font=("none", 11, "bold"))
        self.preview_text.pack(fill=X, expand=True, pady=(0, 4))

        btn_row = ttk.Frame(bottom)
        btn_row.pack(fill=X)
        ttk.Button(btn_row, text="Copy",
                   command=self._copy_output).pack(side=LEFT, padx=2)
        ttk.Checkbutton(btn_row, text="Dwedic Runes",
                        variable=self.runic_var,
                        command=self._update_preview).pack(side=RIGHT, padx=2)

        # Middle: scrollable form area
        # Use a canvas + scrollbar for the middle so complex forms don't clip
        canvas = Canvas(self, bg="black", highlightthickness=0, height=340)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.form_frame = ttk.Frame(canvas)
        self._form_window = canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        self.form_frame.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._canvas = canvas

    def _on_type_change(self):
        # Map display label back to internal type key
        label = self.stype_var.get()
        for key, value in self.SENTENCE_TYPES:
            if key == label:
                self.stype_var.set(value)
                break
        self._render_form_for_type()
        self._update_preview()

    def _render_form_for_type(self):
        # Clear dynamic widgets
        for w in self._dynamic_widgets:
            w.destroy()
        self._dynamic_widgets = []
        self.object_np = None
        self.oblique_list = None

        stype = self.stype_var.get()
        # If the value is still a display label, try to normalize
        if stype not in ("verbal", "copular", "imperative", "question_yn", "question_wh"):
            for key, value in self.SENTENCE_TYPES:
                if key == stype:
                    stype = value
                    self.stype_var.set(value)
                    break

        if stype == "verbal":
            self._build_verbal_form(qword=False)
        elif stype == "question_yn":
            self._build_verbal_form(qword=False)
        elif stype == "question_wh":
            self._build_verbal_form(qword=True)
        elif stype == "copular":
            self._build_copular_form()
        elif stype == "imperative":
            self._build_imperative_form()

    # ---- Form builders ----

    def _build_verbal_form(self, qword=False):
        row = 0
        if qword:
            lf = ttk.LabelFrame(self.form_frame, text="Question Word", padding=6)
            lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
            self._dynamic_widgets.append(lf)
            cb = ttk.Combobox(lf, textvariable=self.qword_var,
                              values=self.QUESTION_WORDS,
                              state="readonly", width=15)
            cb.pack(side=LEFT, padx=4)
            row += 1

        # Tense + aspect group
        lf = ttk.LabelFrame(self.form_frame, text="Tense & Aspect", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1

        ttk.Label(lf, text="Tense:").grid(row=0, column=0, sticky=W, padx=2)
        for i, (label, val) in enumerate(self.TENSES):
            ttk.Radiobutton(lf, text=label, variable=self.tense_var,
                            value=val).grid(row=0, column=1 + i, sticky=W, padx=4)

        ttk.Checkbutton(lf, text="Perfect (have/had/will have)",
                        variable=self.perfect_var).grid(row=1, column=0, columnspan=3, sticky=W)
        ttk.Checkbutton(lf, text="Progressive (-ing)",
                        variable=self.progressive_var).grid(row=1, column=3, columnspan=2, sticky=W)
        ttk.Checkbutton(lf, text="Negation (un-)",
                        variable=self.negation_var).grid(row=2, column=0, columnspan=3, sticky=W)

        # Subject
        lf = ttk.LabelFrame(self.form_frame, text="Subject", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1

        ttk.Radiobutton(lf, text="Pronoun:", variable=self.subject_type_var,
                        value="pronoun").grid(row=0, column=0, sticky=W)
        pcb = ttk.Combobox(lf, textvariable=self.subject_pronoun_var,
                           values=self.PRONOUNS, state="readonly", width=8)
        pcb.grid(row=0, column=1, sticky=W, padx=4)

        ttk.Radiobutton(lf, text="Proper name:", variable=self.subject_type_var,
                        value="proper").grid(row=1, column=0, sticky=W)
        ttk.Entry(lf, textvariable=self.subject_proper_var, width=20
                  ).grid(row=1, column=1, sticky=W, padx=4)

        # Verb
        lf = ttk.LabelFrame(self.form_frame, text="Verb", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1

        ttk.Label(lf, text="Verb:").grid(row=0, column=0, sticky=W, padx=2)
        vcb = ttk.Combobox(lf, textvariable=self.verb_var,
                           values=self.lex.english_labels_of_class("verb"),
                           width=30)
        vcb.grid(row=0, column=1, sticky=W, padx=4)

        # Object (optional noun phrase)
        obj_frame = NounPhraseBuilder(self.form_frame, self.lex,
                                       title="Object (optional)",
                                       on_change=self._update_preview)
        obj_frame.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(obj_frame)
        self.object_np = obj_frame
        row += 1

        # Modifiers (adverbials — adverbs and prepositional phrases)
        obliques = ObliqueList(self.form_frame, self.lex,
                               on_change=self._update_preview)
        obliques.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(obliques)
        self.oblique_list = obliques
        row += 1

    def _build_copular_form(self):
        row = 0
        # Subject
        lf = ttk.LabelFrame(self.form_frame, text="Subject", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1
        ttk.Label(lf, text="Pronoun:").grid(row=0, column=0, sticky=W)
        ttk.Combobox(lf, textvariable=self.cop_subj_pronoun_var,
                     values=self.PRONOUNS, state="readonly", width=8
                     ).grid(row=0, column=1, sticky=W, padx=4)

        # Copula
        lf = ttk.LabelFrame(self.form_frame, text="Copula", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1
        ttk.Combobox(lf, textvariable=self.cop_copula_var,
                     values=self.COPULAS, state="readonly", width=10
                     ).pack(side=LEFT, padx=4)

        # Predicate (adjective for simple case)
        lf = ttk.LabelFrame(self.form_frame, text="Predicate (adjective)", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1
        ttk.Label(lf, text="Adjective:").grid(row=0, column=0, sticky=W)
        ttk.Combobox(lf, textvariable=self.cop_pred_adj_var,
                     values=self.lex.english_labels_of_class("adjective"),
                     width=25).grid(row=0, column=1, sticky=W, padx=4)

    def _build_imperative_form(self):
        row = 0
        # Tense (present = immediate, future = standing order)
        lf = ttk.LabelFrame(self.form_frame, text="Command Type", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1
        ttk.Radiobutton(lf, text="Immediate (Aina-)", variable=self.imp_tense_var,
                        value="present").pack(anchor=W)
        ttk.Radiobutton(lf, text="Standing / oath / law (Enn-)",
                        variable=self.imp_tense_var,
                        value="future").pack(anchor=W)
        ttk.Checkbutton(lf, text="Negation (un-) — prohibition",
                        variable=self.imp_negation_var).pack(anchor=W)

        # Verb
        lf = ttk.LabelFrame(self.form_frame, text="Verb", padding=6)
        lf.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(lf)
        row += 1
        ttk.Combobox(lf, textvariable=self.imp_verb_var,
                     values=self.lex.english_labels_of_class("verb"),
                     width=25).pack(side=LEFT, padx=4)

        # Object
        obj_frame = NounPhraseBuilder(self.form_frame, self.lex,
                                       title="Object (optional)",
                                       on_change=self._update_preview)
        obj_frame.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(obj_frame)
        self.object_np = obj_frame
        row += 1

        # Modifiers
        obliques = ObliqueList(self.form_frame, self.lex,
                               on_change=self._update_preview)
        obliques.grid(row=row, column=0, sticky=EW, padx=4, pady=3)
        self._dynamic_widgets.append(obliques)
        self.oblique_list = obliques

    # ---- State wiring ----

    def _wire_state_changes(self):
        for var in (self.tense_var, self.perfect_var, self.progressive_var,
                    self.negation_var, self.subject_type_var,
                    self.subject_pronoun_var, self.subject_proper_var,
                    self.verb_var, self.qword_var,
                    self.cop_subj_pronoun_var, self.cop_copula_var,
                    self.cop_pred_adj_var, self.imp_tense_var,
                    self.imp_verb_var, self.imp_negation_var):
            var.trace_add("write", lambda *a: self._update_preview())

    # ---- Preview / rendering ----

    def _build_sentence_dict(self):
        """Assemble a sentence dict from current form state. May return None."""
        stype = self.stype_var.get()

        if stype in ("verbal", "question_yn", "question_wh"):
            return self._build_verbal_dict(
                is_question=(stype in ("question_yn", "question_wh")),
                is_wh=(stype == "question_wh"),
            )
        elif stype == "copular":
            return self._build_copular_dict()
        elif stype == "imperative":
            return self._build_imperative_dict()
        return None

    def _build_verbal_dict(self, is_question=False, is_wh=False):
        # Verb required
        english_verb = self.verb_var.get().strip()
        if not english_verb:
            return None
        # Fall back to typed value if not in dictionary
        dwed_verb = self.lex.translate_one(english_verb) or english_verb

        # Subject
        if self.subject_type_var.get() == "pronoun":
            subject = {"type": "pronoun", "value": self.subject_pronoun_var.get()}
        else:
            name = self.subject_proper_var.get().strip()
            if not name:
                return None
            subject = {"type": "proper", "value": name}

        d = {
            "type": "question" if is_question else "verbal",
            "tense": self.tense_var.get(),
            "perfect": bool(self.perfect_var.get()),
            "progressive": bool(self.progressive_var.get()),
            "negation": bool(self.negation_var.get()),
            "subject": subject,
            "verb": dwed_verb,
        }

        if is_wh:
            d["question_word"] = self.qword_var.get()

        # Object (optional)
        if self.object_np:
            obj = self.object_np.to_dict()
            if obj:
                d["object"] = obj

        # Modifiers (adverbials — adverbs and prepositional phrases)
        if self.oblique_list:
            obliques = self.oblique_list.to_list()
            if obliques:
                d["obliques"] = obliques

        return d

    def _build_copular_dict(self):
        adj_english = self.cop_pred_adj_var.get().strip()
        if not adj_english:
            return None
        adj_dwed = self.lex.translate_one(adj_english) or adj_english

        return {
            "type": "copular",
            "subject": {"type": "pronoun", "value": self.cop_subj_pronoun_var.get()},
            "copula": self.cop_copula_var.get(),
            "predicate": {"type": "adjective", "value": adj_dwed},
        }

    def _build_imperative_dict(self):
        english_verb = self.imp_verb_var.get().strip()
        if not english_verb:
            return None
        dwed_verb = self.lex.translate_one(english_verb) or english_verb

        d = {
            "type": "imperative",
            "tense": self.imp_tense_var.get(),
            "verb": dwed_verb,
            "negation": bool(self.imp_negation_var.get()),
        }

        if self.object_np:
            obj = self.object_np.to_dict()
            if obj:
                d["object"] = obj

        # Modifiers
        if self.oblique_list:
            obliques = self.oblique_list.to_list()
            if obliques:
                d["obliques"] = obliques

        return d

    def _update_preview(self):
        sentence = self._build_sentence_dict()
        if sentence is None:
            output = "(fill in required fields...)"
        else:
            try:
                output = render(sentence)
            except Exception as e:
                output = f"(render error: {e})"

        if self.runic_var.get() and not output.startswith("("):
            output = english_to_runic(output)

        self.preview_text.delete("1.0", END)
        self.preview_text.insert(END, output)

    def _copy_output(self):
        text = self.preview_text.get("1.0", END).strip()
        if text and not text.startswith("("):
            self.clipboard_clear()
            self.clipboard_append(text)


# =============================================================================
# RUNES TAB
# =============================================================================

class RunesTab(ttk.Frame):
    """Live transliteration: whatever is typed above appears in runes below."""

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text="Common -> ᚱᚢᚾᛖᛊ",
                  font="none 12 bold").pack(pady=(0, 8))

        self.entry_text = scrolledtext.ScrolledText(
            self, width=40, height=10, wrap=WORD, bg="white")
        self.entry_text.pack(fill=BOTH, expand=True)
        # <<Modified>> also catches paste, cut, and undo, which key events miss.
        self.entry_text.bind("<<Modified>>", self._on_modified)

        self.output_text = scrolledtext.ScrolledText(
            self, width=40, height=10, wrap=WORD, bg="white",
            font="none 12 bold", state=DISABLED)
        self.output_text.pack(fill=BOTH, expand=True, pady=(8, 4))

        ttk.Button(self, text="Copy", command=self._copy_output).pack(side=LEFT)

    def _on_modified(self, event=None):
        # Tk only fires <<Modified>> again after the flag has been reset.
        if not self.entry_text.edit_modified():
            return
        self.entry_text.edit_modified(False)

        output = english_to_runic(self.entry_text.get("1.0", "end-1c"))
        self.output_text.configure(state=NORMAL)
        self.output_text.delete("1.0", END)
        self.output_text.insert(END, output)
        self.output_text.configure(state=DISABLED)

    def _copy_output(self):
        text = self.output_text.get("1.0", "end-1c")
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)


# =============================================================================
# APPLICATION SHELL
# =============================================================================

class DwedTranslatorApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Dwed Translator v3.2")
        self.geometry("560x720")
        self.resizable(True, True)

        apply_theme(self)

        lexicon = DwedLexicon(DICTIONARY_FILE)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=BOTH, expand=True, padx=6, pady=6)

        self.dictionary_tab = DictionaryTab(notebook, lexicon)
        self.sentence_tab = SentenceBuilderTab(notebook, lexicon)
        self.runes_tab = RunesTab(notebook)

        notebook.add(self.dictionary_tab, text="Dictionary")
        notebook.add(self.sentence_tab, text="Sentence Builder")
        notebook.add(self.runes_tab, text="Runes")


if __name__ == "__main__":
    try:
        app = DwedTranslatorApp()
        app.mainloop()
    except Exception:
        # Show startup errors instead of letting a double-clicked console vanish.
        import traceback
        details = traceback.format_exc()
        print(details)
        try:
            from tkinter import messagebox
            Tk().withdraw()
            messagebox.showerror("Dwed Translator failed to start", details)
        except Exception:
            input("Press Enter to close...")
