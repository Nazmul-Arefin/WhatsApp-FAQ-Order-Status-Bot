import json
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
DATA_DIR = Path(__file__).parent / "data"
FAQ_FILE = DATA_DIR / "faq.json"
ORDERS_FILE = DATA_DIR / "orders.json"
class KnowledgeBase:
    def __init__(self):
        self._faq = self._load_json(FAQ_FILE)
        self._orders = self._load_json(ORDERS_FILE)

    @staticmethod
    def _load_json(path: Path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def _save_json(path: Path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Public APIs for admin edits
    def get_faq(self):
        return self._faq
    def set_faq(self, faq: Dict):
        self._faq = faq
        self._save_json(FAQ_FILE, self._faq)
    def get_orders(self):
        return self._orders
    def set_orders(self, orders: Dict):
        self._orders = orders
        self._save_json(ORDERS_FILE, self._orders)

    # Runtime helpers
    def match_faq(self, text: str) -> Optional[str]:
        text_l = text.lower()
        for item in self._faq.get("items", []):
            for kw in item.get("keywords", []):
                if kw.lower() in text_l:
                    return item.get("answer")
        return None
    def lookup_order(self, text: str) -> Optional[Tuple[str, Dict]]:
        # Try explicit pattern: order #ABC123 or order 12345
        m = re.search(r"order\s*#?([A-Za-z0-9_-]{3,})", text, re.IGNORECASE)
        order_id = m.group(1) if m else None
        # Or loose: a token that looks like an ID
        if not order_id:
            m2 = re.search(r"\b([A-Za-z0-9]{5,})\b", text)
            order_id = m2.group(1) if m2 else None
        if not order_id:
            return None
        order = self._orders.get("orders", {}).get(order_id)
        if order:
            return order_id, order
        return None
    
    def detect_intent(text: str, kb: KnowledgeBase) -> Tuple[str, Dict]:
        # Heuristic: if mentions order/id, treat as order intent first
        order = kb.lookup_order(text)

        if order:
            order_id, details = order
            return "order", {"order_id": order_id, **details}
        # Else try FAQ keywords
        ans = kb.match_faq(text)
        if ans:
            return "faq", {"answer": ans}
        return "fallback", {"message": "I couldn't find that. A human agent will follow up."}