# Simple rule-based router:
# - SMALL_TALK for greetings/thanks/etc.
# - DOC_QA otherwise.
# This is intentionally simple for learning; later you can swap with a Gemini classifier.

SMALL_TALK_TRIGGERS = {
    "hi", "hello", "hey", "how are you", "thanks", "thank you", "good morning",
    "good evening", "yo", "sup", "what's up"
}

def detect_intent(user_text: str) -> str:
    t = (user_text or "").strip().lower()
    if not t:
        return "DOC_QA"
    # basic greeting/thanks detector
    for trig in SMALL_TALK_TRIGGERS:
        if trig in t:
            return "SMALL_TALK"
    # if the user mentions docs/load/upload, keep it conversational (we'll still answer)
    if "upload" in t or "document" in t or "file" in t:
        return "SMALL_TALK"
    return "DOC_QA"
