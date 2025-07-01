from rapidfuzz import fuzz
import re
from mitmproxy import ctx

def normalize(text):
    """Normalize text by decoding escape sequences and reducing whitespace."""
    try:
        text = bytes(text, "utf-8").decode("unicode_escape")
    except Exception:
        pass
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def fuzzy_match_snippet_parts(needle, haystack, window_size=300, step=50, threshold=51, min_match_ratio=0.1, min_match_length=30):
    """
    Slides a window over `needle` and tries to match each chunk with `haystack`.
    Filters out short matches that can skew scores (e.g. "false").
    
    Returns:
        match_found (bool),
        best_score (int),
        best_snippet (str)
    """
    max_score = 0
    best_snippet = ""
    match_found = False

    for i in range(0, len(needle), step):
        window = needle[i:i+window_size]
        if not window:
            continue
        score = fuzz.partial_ratio(window, haystack)

        # Enforce length-based validation
        match_is_significant = (
            len(window) >= min_match_length and
            len(window) / max(len(haystack), 1) >= min_match_ratio
        )

        if score > max_score and match_is_significant:
            max_score = score
            best_snippet = window
        if score >= threshold and match_is_significant:
            match_found = True

    return match_found, max_score, best_snippet


def fuzzydiff_in_file(file_path, input_text, threshold=51):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        full_code = f.read()

    needle = normalize(full_code)
    haystack = normalize(input_text)

    match, best_score, best_snippet = fuzzy_match_snippet_parts(needle, haystack, threshold=threshold)

    return (match), best_score, best_snippet