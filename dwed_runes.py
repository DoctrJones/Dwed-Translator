"""
Dwed runes — Latin-to-runic transliteration (ahld'rhun).

Moved out of UTA_DWED_Class_v3_Claude.py so the translator no longer needs
the legacy Excel libraries just to draw runes.
"""

FUTHARK_ALPHABET = {
    'a': 'ᚨ', 'b': 'ᛒ', 'c': 'ᚲ', 'd': 'ᛞ', 'e': 'ᛖ', 'f': 'ᚠ', 'g': 'ᚷ', 'h': 'ᚺ',
    'i': 'ᛁ', 'j': 'ᛃ', 'k': 'ᚲ', 'l': 'ᛚ', 'm': 'ᛗ', 'n': 'ᚾ', 'o': 'ᛟ', 'p': 'ᛈ',
    'q': 'ᚲ', 'r': 'ᚱ', 's': 'ᛊ', 't': 'ᛏ', 'u': 'ᚢ', 'v': 'ᚹ', 'w': 'ᚹ', 'y': 'ᛃ',
    'z': 'ᛉ', ' ': ' ',
}


def english_to_runic(text):
    """Transliterate text to Dwedic runes; characters without a rune pass through."""
    return ''.join(FUTHARK_ALPHABET.get(char, char) for char in text.lower())
