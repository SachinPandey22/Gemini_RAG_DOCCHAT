import os
from dotenv import load_dotenv
import google.generativeai as genai
from .prompts import build_small_talk_prompt, build_doc_qa_prompt

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Missing Gemini API key.")
genai.configure(api_key=api_key)

# Choose a fast, capable model. You can swap to 1.5 Pro if you prefer.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def generate_small_talk(history, user_text) -> str:
    """
    Returns a short natural reply for greetings / chit-chat.
    """
    prompt = build_small_talk_prompt(history, user_text)
    resp = genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
    return (resp.text or "").strip()

def generate_doc_answer(history, user_text, contexts) -> str:
    """
    Returns a grounded answer with a 'Citations' section.
    """
    prompt = build_doc_qa_prompt(history, user_text, contexts)
    resp = genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
    return (resp.text or "").strip()
