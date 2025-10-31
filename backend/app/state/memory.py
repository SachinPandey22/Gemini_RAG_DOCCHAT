from collections import defaultdict, deque
from typing import Deque, Dict, List, Tuple

# Namespace -> deque of (role, text)
_HISTORY: Dict[str, Deque[Tuple[str, str]]] = defaultdict(lambda: deque(maxlen=10))

def add_turn(namespace: str, role: str, text: str):
    _HISTORY[namespace].append((role, text))

def get_recent(namespace: str, max_turns: int = 5) -> List[Tuple[str, str]]:
    hist = _HISTORY.get(namespace, deque())
    # Return only the last `max_turns` messages
    return list(hist)[-max_turns:]
