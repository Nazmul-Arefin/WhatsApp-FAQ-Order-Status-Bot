import os
import json
from typing import Any, Dict
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from meta_api import MetaAPIClient
from intents import KnowledgeBase, detect_intent

load_dotenv()

app = FastAPI(title="WhatsApp FAQ & Order Status Bot")

# CORS for Streamlit dashboard
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Config
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "verify_me")
TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
GRAPH_VER = os.getenv("META_GRAPH_VERSION", "v20.0")
DEFAULT_TEMPLATE = os.getenv("DEFAULT_TEMPLATE_NAME", "hello_world")
LANG = os.getenv("TEMPLATE_LANG", "en_US")

meta = MetaAPIClient(TOKEN, PHONE_ID, GRAPH_VER)
kb = KnowledgeBase()

@app.get("/health")
def health():
    return {"ok": True}

# Webhook verification (GET)
@app.get("/webhook")
def verify_webhook(mode: str | None = None, challenge: str | None = None,
                  verify_token: str | None = None, hub_mode: str | None = None,
                  hub_verify_token: str | None = None, hub_challenge: str | None = None):
    # Support both styles: ?hub.mode=&hub.verify_token=&hub.challenge=
    mode = mode or hub_mode
    token = verify_token or hub_verify_token
    challenge = challenge or hub_challenge
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge or "", media_type="text/plain")
    return Response(status_code=403)

# Webhook receiver (POST)
@app.post("/webhook")
async def webhook(req: Request):
    body = await req.json()
    try:
        entry = body.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        contacts = value.get("contacts", [])
        messages = value.get("messages", [])

        if not messages:
            return {"received": True}

        message = messages[0]
        from_wa = message.get("from")  # sender phone in international format
        text = message.get("text", {}).get("body") if message.get("type") == "text" else None

        if not text:
            # Non-text: politely fallback
            meta.send_text(from_wa, "Please send a text message (FAQ or order query). 😊")
            return {"received": True}

        intent, data = detect_intent(text, kb)
        if intent == "faq":
            meta.send_text(from_wa, data["answer"])
        elif intent == "order":
            reply = (
                f"Order #{data['order_id']}\n"
                f"Status: {data.get('status','N/A')}\n"
                f"ETA: {data.get('eta','N/A')}\n"
                f"Carrier: {data.get('carrier','N/A')}\n"
            )
            meta.send_text(from_wa, reply)
        else:
            meta.send_text(from_wa, "I couldn't find that. A human agent will follow up.")

        return {"handled": True}
    except Exception as e:
        # Never fail webhook delivery: return 200
        print("Webhook error:", e)
        return {"handled": False}

# --- Admin/Utility APIs for dashboard ---
class SendTemplateBody(BaseModel):
    to: str
    template_name: str | None = None
    lang_code: str | None = None
    components: list[Any] | None = None

@app.post("/send_template")
def send_template(body: SendTemplateBody):
    name = body.template_name or DEFAULT_TEMPLATE
    lang = body.lang_code or LANG
    resp = meta.send_template(body.to, name, lang, body.components)
    return resp

class SendTextBody(BaseModel):
    to: str
    text: str

@app.post("/send_text")
def send_text(body: SendTextBody):
    resp = meta.send_text(body.to, body.text)
    return resp

class FAQUpdate(BaseModel):
    items: list[dict]

@app.get("/admin/faq")
def get_faq():
    return kb.get_faq()

@app.put("/admin/faq")
def put_faq(update: FAQUpdate):
    kb.set_faq(update.model_dump())
    return {"ok": True}

@app.get("/admin/orders")
def get_orders():
    return kb.get_orders()
