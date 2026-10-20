"""
Dwed Lexicon — dictionary loader and query helper for both translator tabs.

Loads the dictionary CSV (DICTIONARY_dwed.csv) using only the standard library.

CSV layout (UTF-8, first row is the header):
    english   English word/phrase
    dwed      Dwed translation
    class     word class (noun, verb, adjective, ... — see README)
    status    "auto" (auto-tagged, high confidence), "review" (class needs
              checking), or "verified" (checked by a human)
    notes     free text (etymology, usage), optional

Every column that is not one of the reserved columns (class, status, notes)
is treated as a language. To add a language, add a column — it will appear in
the Dictionary tab's source/target dropdowns automatically.

Intentional synonyms get one row each (e.g. "the" -> "da" and "the" -> "ok").
"""

import csv
from collections import defaultdict

RESERVED_COLUMNS = ("class", "status", "notes")
NOT_FOUND = "[x]"


def load_dictionary(path):
    """Read the dictionary CSV. Returns (languages, rows).

    languages: list of language column names, in file order
    rows:      list of dicts, one per entry, with whitespace stripped
    """
    # utf-8-sig accepts files with or without the byte-order mark Excel adds.
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        languages = [c for c in reader.fieldnames if c not in RESERVED_COLUMNS]
        rows = [{k: (v or "").strip() for k, v in row.items() if k is not None}
                for row in reader]
    return languages, rows


class DwedLexicon:
    """Loads the dictionary and provides class-filtered and per-language lookups."""

    def __init__(self, dictionary_path):
        self.path = dictionary_path
        self._languages, self._rows = load_dictionary(dictionary_path)

        # word_class -> list of (english, dwed) tuples, sorted by english
        self._by_class = defaultdict(list)
        # english -> list of dwed forms (for polysemy)
        self._english_index = defaultdict(list)

        self._index()

    def _index(self):
        for row in self._rows:
            english = row.get("english", "")
            dwed = row.get("dwed", "")
            if not english or not dwed:
                continue
            word_class = row.get("class") or "noun"

            self._by_class[word_class].append((english, dwed))
            self._english_index[english.lower()].append(dwed)

        # Sort each class by English word for nice dropdown ordering
        for cls in self._by_class:
            self._by_class[cls].sort(key=lambda pair: pair[0].lower())

    # ---- Sentence Builder queries ----

    def classes(self):
        """Return the list of word classes present in the dictionary."""
        return sorted(self._by_class.keys())

    def words_of_class(self, word_class):
        """Return a list of (english, dwed) tuples for the given word class."""
        return list(self._by_class.get(word_class, []))

    def english_labels_of_class(self, word_class):
        """Return English labels for dropdowns, in sorted order."""
        return [pair[0] for pair in self._by_class.get(word_class, [])]

    def translate(self, english):
        """Look up English -> Dwed. Returns list of Dwed forms (may be > 1)."""
        return list(self._english_index.get(english.lower().strip(), []))

    def translate_one(self, english):
        """Look up English -> first Dwed form. Returns None if not found."""
        matches = self.translate(english)
        return matches[0] if matches else None

    # ---- Dictionary tab queries ----

    def languages(self):
        """Return the language column names, in file order."""
        return list(self._languages)

    def translate_tokens(self, tokens, source, target):
        """Word-for-word substitution for the Dictionary tab.

        Each token is matched exactly against the source column. One match
        yields the target word; several matches yield "[ a , b ]"; no match
        (or an empty target cell) yields "[x]". Returns a list of strings.
        """
        index = defaultdict(list)
        for row in self._rows:
            key = row.get(source, "")
            if key:
                index[key].append(row.get(target, "") or NOT_FOUND)

        out = []
        for token in tokens:
            matches = index.get(token)
            if not matches:
                out.append(NOT_FOUND)
            elif len(matches) == 1:
                out.append(matches[0])
            else:
                out.append("[")
                out.append(" , ".join(matches))
                out.append("]")
        return out

    def stats(self):
        """Return a summary dict for debugging."""
        return {cls: len(words) for cls, words in self._by_class.items()}
