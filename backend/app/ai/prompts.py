from typing import List, Dict

def build_small_talk_prompt(history: List[tuple], user_text: str) -> str:
    """
    Keep it friendly, concise, and avoid hallucinations.
    """
    msgs = []
    if history:
        msgs.append("Recent chat:")
        for role, text in history[-4:]:
            who = "User" if role == "user" else "Assistant"
            msgs.append(f"{who}: {text}")
        msgs.append("---")
    msgs.append("Instruction: Reply naturally and briefly.")
    msgs.append(f"User: {user_text}")
    return "\n".join(msgs)

def build_doc_qa_prompt(
    history: List[tuple],
    user_text: str,
    contexts: List[Dict[str, str]]
) -> str:
    """
    Grounded answering template.
    - contexts: list of dicts with keys: text, filename, page (optional)
    """
    msgs = []
    if history:
        msgs.append("Recent chat (for context only; do NOT cite these):")
        for role, text in history[-4:]:
            who = "User" if role == "user" else "Assistant"
            msgs.append(f"{who}: {text}")
        msgs.append("---")

    msgs.append(
        "You are a helpful assistant. Use ONLY the provided Context Snippets to answer the user."
        " If the answer is not clearly contained in the snippets, say: \"I don't know.\""
        " Always include a 'Citations' section listing the sources you used."
        " Citations should be in the form: [filename (and page if available)]."
    )
    msgs.append(f"User question: {user_text}\n")
    msgs.append("Context Snippets:")
    for i, c in enumerate(contexts, 1):
        fn = c.get("filename", "unknown")
        pg = c.get("page")
        head = f"[{i}] {fn}" + (f" (page {pg})" if pg else "")
        msgs.append(head)
        msgs.append(c.get("text", "")[:1200])  # limit each snippet length
        msgs.append("---")
    msgs.append(
        "Format your response as:\n"
        "Answer:\n"
        "<your concise grounded answer>\n\n"
        "Citations:\n"
        "- <filename (page X)>\n"
        "- <filename>\n"
    )
    return "\n".join(msgs)
