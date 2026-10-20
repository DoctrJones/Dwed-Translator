"""
Dwed Sentence Renderer
======================
Pure-logic module that takes a structured sentence description (a Python dict)
and produces a grammatically-correct Dwed string according to the rules laid
out in the Codex of Dwarven Grammar (4th Edition).

No UI, no I/O, no dictionary lookup. This is the compiler. Input goes in as a
fully-specified dict; string comes out. Every rule from the Codex should be
encoded here exactly once.

Design philosophy:
    - Small functions per grammatical rule, mirroring the Codex structure.
    - Input dicts assume English words have ALREADY been translated to Dwed
      by the caller (via dictionary lookup). The renderer's job is grammar,
      not vocabulary.
    - Nothing here silently guesses or "corrects" — if the input is malformed,
      tough shit.

—Benjamin Hansen / Ferek Frostbeard
"""


# =============================================================================
# CONSTANTS — the fixed morphemes from the Codex
# =============================================================================

TENSE_PREFIXES = {
    "past":    "Yno",
    "present": "Aina",
    "future":  "Enn",
}

# Perfect infix. The Codex lists two forms; -nairon- for non-future,
# -naerk- for future. This is a common cross-linguistic pattern (future
# perfect often gets its own marker) and matches the Codex table.
PERFECT_INFIX = {
    "past":    "nairon",
    "present": "nairon",
    "future":  "naerk",
}

# Subject pronouns keyed by English. When multiple Dwed forms exist,
# the shorter/more-fused form is listed first (used by default in the
# tense complex where fusion is prioritized).
SUBJECT_PRONOUNS = {
    "i":    ["K", "Tha"],
    "we":   ["Ut", "Thamar"],
    "you":  ["Othok"],
    "he":   ["Ka"],
    "she":  ["Lon"],
    "it":   ["Ek"],
    "they": ["Korth"],
}

# Possessive pronoun forms — prefix pattern (attaches to possessed noun)
POSSESSIVE_PREFIXES = {
    "i":    "Vo",         # Vo'K, Vo'Tha
    "we":   "Yol",        # Yol'Thamar (also Vo'Ut)
    "you":  "Othok",      # Othok'... uses the pronoun itself as prefix
    "he":   "Vo",         # Vo'Ka
    "she":  "Lon",        # Lon'... (irregular — often uses -edos suffix instead)
    "it":   "Vo",
    "they": "Korth",      # Korth'edos, Vo'Korth
}

# Possessive suffix form (attaches to possessor)
POSSESSIVE_SUFFIXES = {
    "default": "edos",
    "you":     "koss",
    "he":      "oss",
}

DETERMINERS = {
    "the":  "da",     # "ok" also valid; renderer picks "da" as default
    "this": "dak",
    "that": "dag",
    None:   None,     # bare (no determiner)
}

# Adjective suffix — Codex lists -os / -mos / -rum as free variants.
# Default to -os; expose the choice as an option for now.
ADJECTIVE_SUFFIX_DEFAULT = "os"

# Plural marker
PLURAL_SUFFIX = "mar"

# Words that don't take the plural marker (from the Codex)
UNMARKED_PLURALS = {"ruhn"}

# Question words — mapped English → Dwed
QUESTION_WORDS = {
    "what":     "Yir",
    "where":    "Kozrol",
    "why":      "Voki",
    "who":      "Rumol",
    "which":    "Yiik",
    "how":      "Ekor",
    "however":  "Ekorien",
}

# Copulas — three attested variants, selected by phonological flow
COPULAS = ["yol-mer", "va-mer", "moredos"]

# The complementizer
COMPLEMENTIZER = "ke"

# Relative pronouns
RELATIVE_PRONOUNS = {
    "inanimate": "yiik",
    "animate":   "rumol",
}

# Negation prefix
NEGATION = "Un"


# =============================================================================
# CORE BUILDERS — atomic pieces of the grammar
# =============================================================================

def render_subject_pronoun(subject, form_preference="short"):
    """Resolve an English subject pronoun to its Dwed form.

    Args:
        subject: dict like {"type": "pronoun", "value": "I"}
                 or         {"type": "noun", "value": "Kornazkarumm"}  (already-Dwed)
                 or         {"type": "proper", "value": "Bjorn"}
        form_preference: "short" (K, Ut) or "long" (Tha, Thamar) for pronouns
                         with two attested forms.

    Returns:
        The Dwed subject string (no apostrophes, ready to fuse into the complex).
    """
    stype = subject["type"]

    if stype == "pronoun":
        forms = SUBJECT_PRONOUNS.get(subject["value"].lower())
        if not forms:
            raise ValueError(f"Unknown pronoun: {subject['value']!r}")
        form = forms[0] if form_preference == "short" else forms[-1]
        # Pronouns inside the tense complex are lowercase EXCEPT for 1st-person
        # singular "K", which is always uppercase (following Codex convention).
        # The tense prefix at the head of the complex carries the capital.
        if form != "K":
            form = form.lower()
        return form

    if stype in ("noun", "proper"):
        # Already a Dwed word (e.g., "Kornazkarumm", "Bjorn")
        return subject["value"]

    raise ValueError(f"Unknown subject type: {stype!r}")


def render_tense_complex(tense, subject, perfect=False, negated=False,
                          verb_marker="az", pronoun_form="short"):
    """Build the fused [TENSE] + [(PERFECT)] + [SUBJECT] + [VERB-MARKER] unit.

    This is THE central construction of Dwed grammar. Codex Part 2.

    Args:
        tense: "past" | "present" | "future"
        subject: subject dict (see render_subject_pronoun)
        perfect: bool — include the perfect infix
        negated: bool — prefix Un- to the whole complex
        verb_marker: "az" (default) or "ok"
        pronoun_form: passed through to render_subject_pronoun

    Returns:
        Fused tense complex, e.g. "Aina'K'az" or "Yno'nairon'lon'az".
    """
    if tense not in TENSE_PREFIXES:
        raise ValueError(f"Unknown tense: {tense!r}")

    parts = [TENSE_PREFIXES[tense]]
    if perfect:
        parts.append(PERFECT_INFIX[tense])
    parts.append(render_subject_pronoun(subject, pronoun_form))

    complex_str = "'".join(parts) + "'" + verb_marker

    if negated:
        complex_str = f"{NEGATION}'{complex_str}"

    return complex_str


def render_imperative_head(tense, verb, negated=False):
    """Build the [TENSE] + VERB head of an imperative clause. Codex Part 8.

    Subject drops in imperatives — only tense and verb remain.

    Args:
        tense: "present" (immediate command) or "future" (standing order)
        verb: Dwed verb root
        negated: bool — prohibitions get Un- prefix

    Returns:
        e.g. "Aina'strol", "Un'Enn'kavok"
    """
    if tense not in ("present", "future"):
        raise ValueError(f"Imperative tense must be 'present' or 'future', got {tense!r}")

    head = f"{TENSE_PREFIXES[tense]}'{verb}"
    if negated:
        head = f"{NEGATION}'{head}"
    return head


def render_adjective(word, suffix=ADJECTIVE_SUFFIX_DEFAULT):
    """Attach the adjective suffix to a root. Codex Part 4."""
    if suffix not in ("os", "mos", "rum"):
        raise ValueError(f"Adjective suffix must be one of os/mos/rum, got {suffix!r}")
    return f"{word}'{suffix}"


def render_plural(word):
    """Attach the plural marker unless the word is on the unmarked list."""
    if word.lower() in UNMARKED_PLURALS:
        return word
    return f"{word}'{PLURAL_SUFFIX}"


def render_possessive(possessor, style="prefix"):
    """Render a possessive form. Codex Part 3.

    Two patterns, both legal (Codex explicitly permits speaker choice):

        "prefix"  → Vo'K, Yol'Thamar (attaches to the following possessed noun)
        "suffix"  → Bjorn'edos, Othok'koss (attaches to the possessor)

    Args:
        possessor: dict like {"type": "pronoun", "value": "I"}
                          or {"type": "proper", "value": "Bjorn"}
        style: "prefix" or "suffix"

    Returns:
        The possessive form, ready to be placed in a noun phrase.
        Prefix form ends with ' (apostrophe) since it fuses forward.
        Suffix form is a standalone word.
    """
    ptype = possessor["type"]
    pval = possessor["value"]

    if style == "prefix":
        if ptype == "pronoun":
            prefix = POSSESSIVE_PREFIXES.get(pval.lower())
            if not prefix:
                raise ValueError(f"No possessive prefix for pronoun: {pval!r}")
            # For pronouns with two subject forms, the prefix combines
            # with the short pronoun form: Vo + K → Vo'K
            pronoun_forms = SUBJECT_PRONOUNS.get(pval.lower(), [])
            if pronoun_forms and prefix != pval.capitalize():
                return f"{prefix}'{pronoun_forms[0]}"
            return f"{prefix}"
        else:
            raise ValueError(f"Prefix style requires a pronoun possessor, got {ptype!r}")

    elif style == "suffix":
        # Suffix picks based on the possessor
        if ptype == "pronoun":
            key = pval.lower()
            suffix = POSSESSIVE_SUFFIXES.get(key, POSSESSIVE_SUFFIXES["default"])
            pronoun_forms = SUBJECT_PRONOUNS.get(key, [])
            base = pronoun_forms[-1] if pronoun_forms else pval
            return f"{base}'{suffix}"
        elif ptype == "proper":
            return f"{pval}'{POSSESSIVE_SUFFIXES['default']}"
        else:
            raise ValueError(f"Unknown possessor type: {ptype!r}")

    raise ValueError(f"Possessive style must be 'prefix' or 'suffix', got {style!r}")


def render_noun_phrase(np):
    """Assemble a noun phrase per Codex Part 4.

    Order: [DETERMINER or POSSESSIVE-prefix] [NOUN] [ADJECTIVE(s)] [POSSESSOR-suffix phrase]

    Args:
        np: dict with keys (all optional except "noun"):
            - determiner: "the" | "this" | "that" | None
            - possessive: {"possessor": {...}, "style": "prefix"|"suffix"} or None
            - noun: Dwed noun root (required)
            - plural: bool
            - adjectives: list of Dwed adjective roots
            - adj_suffix: which suffix to use for adjectives ("os"/"mos"/"rum")

    Returns:
        Assembled noun phrase string.
    """
    parts = []

    # Determiner OR possessive-prefix at the front (they compete for the same slot)
    poss = np.get("possessive")
    det = np.get("determiner")

    if poss and poss.get("style") == "prefix":
        # Prefix possessive: e.g. "Vo'K" (possessive + pronoun form).
        # It stands as its own word BEFORE the noun, separated by a space.
        prefix_str = render_possessive(poss["possessor"], style="prefix")
        # Optionally allow a determiner before the possessive (Codex example:
        # "dak vo'K gord ardoth'os" — this my red house)
        if det:
            parts.append(DETERMINERS[det])
        parts.append(prefix_str)
        noun = np["noun"]
        if np.get("plural"):
            noun = render_plural(noun)
        parts.append(noun)
    else:
        # No prefix possessive — determiner (if any) stands alone before noun
        if det:
            parts.append(DETERMINERS[det])
        noun = np["noun"]
        if np.get("plural"):
            noun = render_plural(noun)
        parts.append(noun)

    # Adjectives — always post-nominal, each with adjective suffix
    adj_suffix = np.get("adj_suffix", ADJECTIVE_SUFFIX_DEFAULT)
    for adj in np.get("adjectives", []):
        parts.append(render_adjective(adj, suffix=adj_suffix))

    # Suffix-style possessive comes BEFORE the noun (Bjorn'edos Kharadun)
    # This is handled by placing the possessor at the head of the NP
    if poss and poss.get("style") == "suffix":
        suffix_str = render_possessive(poss["possessor"], style="suffix")
        parts.insert(0, suffix_str)

    return " ".join(parts)


def render_prepositional_phrase(pp):
    """Build a prepositional phrase per Codex Part 10.

    Args:
        pp: dict with keys:
            - preposition: Dwed preposition (e.g. "nir", "oz", "narh")
            - object: a noun phrase dict (see render_noun_phrase)
            - fuse: bool — optionally fuse preposition with determiner
                    (nir + da → nirda). Only applies when object has a determiner.

    Returns:
        Assembled PP string.
    """
    prep = pp["preposition"]
    obj = pp["object"]
    fuse = pp.get("fuse", False)

    obj_str = render_noun_phrase(obj)

    if fuse and obj.get("determiner") and not obj.get("possessive"):
        # Fuse preposition with leading determiner
        det_str = DETERMINERS[obj["determiner"]]
        if obj_str.startswith(det_str + " "):
            rest = obj_str[len(det_str) + 1:]
            return f"{prep}{det_str} {rest}"

    return f"{prep} {obj_str}"


# =============================================================================
# SENTENCE-LEVEL RENDERERS — one per sentence type
# =============================================================================

def render_verbal(s):
    """Render a verbal sentence. Codex Part 8 (Declarative).

    Structure: [TENSE COMPLEX] [VERB] [OBJECT] [OBLIQUE PHRASES]
    """
    tc = render_tense_complex(
        tense=s["tense"],
        subject=s["subject"],
        perfect=s.get("perfect", False),
        negated=s.get("negation", False),
        verb_marker=s.get("verb_marker", "az"),
        pronoun_form=s.get("pronoun_form", "short"),
    )

    verb = s["verb"]
    if s.get("progressive"):
        verb = f"{verb}'geron"

    parts = [tc, verb]

    if s.get("object"):
        parts.append(render_noun_phrase(s["object"]))

    for oblique in s.get("obliques", []):
        # An oblique can be a prepositional phrase, an adverb, or a noun phrase
        if oblique.get("type") == "prep":
            parts.append(render_prepositional_phrase(oblique))
        elif oblique.get("type") == "adverb":
            parts.append(oblique["value"])
        elif oblique.get("type") == "noun_phrase":
            parts.append(render_noun_phrase(oblique))
        else:
            raise ValueError(f"Unknown oblique type: {oblique.get('type')!r}")

    return " ".join(parts)


def render_copular(s):
    """Render a copular sentence. Codex Part 8.

    Structure: [SUBJECT] [COPULA] [PREDICATE]

    Predicate may be a noun phrase, a prepositional phrase, or an adjective.
    Copular clauses do NOT use the tense complex.
    """
    subject_str = render_noun_phrase(s["subject"]) if isinstance(s["subject"], dict) and "noun" in s["subject"] \
                  else render_subject_pronoun(s["subject"])

    copula = s.get("copula", COPULAS[0])

    pred = s["predicate"]
    if pred["type"] == "noun_phrase":
        pred_str = render_noun_phrase(pred)
    elif pred["type"] == "prep":
        pred_str = render_prepositional_phrase(pred)
    elif pred["type"] == "adjective":
        pred_str = render_adjective(pred["value"], pred.get("suffix", ADJECTIVE_SUFFIX_DEFAULT))
    elif pred["type"] == "bare":
        pred_str = pred["value"]  # a bare Dwed word, no morphology applied
    else:
        raise ValueError(f"Unknown predicate type: {pred['type']!r}")

    return f"{subject_str} {copula} {pred_str}"


def render_imperative(s):
    """Render an imperative. Codex Part 8.

    Structure: [(NEG)] [TENSE] + VERB [OBJECT] [OBLIQUES]

    Subject drops. Present = immediate command; Future = standing order.
    """
    head = render_imperative_head(
        tense=s.get("tense", "present"),
        verb=s["verb"],
        negated=s.get("negation", False),
    )

    parts = [head]

    if s.get("object"):
        parts.append(render_noun_phrase(s["object"]))

    for oblique in s.get("obliques", []):
        if oblique.get("type") == "prep":
            parts.append(render_prepositional_phrase(oblique))
        elif oblique.get("type") == "adverb":
            parts.append(oblique["value"])

    return " ".join(parts)


def render_question(s):
    """Render a question. Codex Part 8.

    Yes/no questions have identical word order to declaratives — only
    punctuation distinguishes them. Wh-questions front the question word.
    """
    q_word_key = s.get("question_word")  # "what", "where", None (yes/no), etc.

    # Build the body (same as a verbal or copular sentence)
    if s.get("clause_type") == "copular":
        body = render_copular(s)
    else:
        body = render_verbal(s)

    if q_word_key:
        q_dwed = QUESTION_WORDS[q_word_key.lower()]
        return f"{q_dwed} {body}"

    return body  # yes/no — punctuation added by the outer render() call


# =============================================================================
# TOP-LEVEL DISPATCH
# =============================================================================

def render(sentence):
    """Render any sentence. Dispatches on 'type' key.

    Args:
        sentence: dict with a "type" key: "verbal" | "copular" | "imperative" | "question"

    Returns:
        The rendered Dwed sentence, ending in appropriate punctuation.
    """
    stype = sentence.get("type")

    if stype == "verbal":
        text = render_verbal(sentence)
        terminator = "."
    elif stype == "copular":
        text = render_copular(sentence)
        terminator = "."
    elif stype == "imperative":
        text = render_imperative(sentence)
        terminator = "!"
    elif stype == "question":
        text = render_question(sentence)
        terminator = "?"
    else:
        raise ValueError(f"Unknown sentence type: {stype!r}")

    # Capitalize first letter if it isn't already (tense complex is already
    # capitalized by convention, but bare-verb imperatives may not be)
    if text and text[0].islower():
        text = text[0].upper() + text[1:]

    return text + terminator
