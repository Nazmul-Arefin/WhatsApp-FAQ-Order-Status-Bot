import os
import requests
from typing import Any, Dict, Optional
class MetaAPIClient:
    def __init__(self, token: str, phone_number_id: str, graph_version: str = "v20.0"):
        self.token = token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/{graph_version}/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    def send_text(self, to: str, text: str) -> Dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        resp = requests.post(self.base_url, headers=self.headers, json=payload,
        timeout=30)
        return {"status_code": resp.status_code, "data": resp.json() if resp.content else {}}

    def send_template(self, to: str, template_name: str, lang_code: str =
        "en_US", components: Optional[list] = None) -> Dict[str, Any]:
        payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
        "name": template_name,
        "language": {"code": lang_code}
        }
        }
        if components:
            payload["template"]["components"] = components
        resp = requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
        return {"status_code": resp.status_code, "data": resp.json() if resp.content else {}}