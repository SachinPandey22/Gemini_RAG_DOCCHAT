import re

_ws_re = re.compile(r"\s+")

def normalize_whitespace(s: str) -> str:
    """Collapse weird whitespace/newlines into single spaces."""
    return _ws_re.sub(" ", s).strip()

def to_words(s: str):
    """Very simple tokenizer by whitespace (enough for learning)."""
    return normalize_whitespace(s).split(" ")

#Help Cleaning text