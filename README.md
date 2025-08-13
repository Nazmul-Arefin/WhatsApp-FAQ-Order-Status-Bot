# WhatsApp FAQ & Order Status Bot

> FastAPI webhook + Streamlit dashboard • Meta WhatsApp Cloud API • Minimal, internship‑ready demo.

## ✨ Features

- **Inbound webhook (FastAPI):** Receives WhatsApp messages, detects intents (FAQ/order), and replies.
- **FAQ lookup (JSON):** Keyword‑based answers from `faq.json`.
- **Mock order status:** Lookup from `orders.json`.
- **Outbound templates:** Send approved WhatsApp templates via Meta Cloud API.
- **Streamlit dashboard:** Send text/templates, test FAQs & orders, edit FAQs.
- **Future‑ready:** Easy to adapt for WATI API.

## 🧱 Project Structure

```
whatsapp-faq-order-bot/
├─ backend/
│  ├─ app.py
│  ├─ meta_api.py
│  ├─ intents.py
│  ├─ data/
│  │  ├─ faq.json
│  │  └─ orders.json
│  ├─ .env.example
│  ├─ requirements.txt
├─ dashboard/
│  ├─ streamlit_app.py
│  ├─ requirements.txt
└─ README.md
```

## 🚀 Quickstart

### Prerequisites

- Python 3.10–3.12
- Meta WhatsApp Cloud API account with test number
- ngrok/cloudflared for webhook tunneling

### 1. Backend

```bash
cd backend
cp .env.example .env  # Fill with token, phone number ID, verify token
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Webhook Tunnel

```bash
ngrok http 8000
```

Set **Callback URL** in Meta: `https://<ngrok-url>/webhook` and Verify Token from `.env`. Subscribe to **messages**.

### 3. Dashboard

```bash
cd ../dashboard
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

Open [http://localhost:8501](http://localhost:8501) and set Backend Base URL to `http://localhost:8000`.

## 📩 API Cheatsheet

```
GET  /health
POST /webhook
POST /send_text
POST /send_template
GET  /admin/faq
PUT  /admin/faq
GET  /admin/orders
```

## 🧠 Architecture

```
Streamlit Dashboard ⇆ Admin APIs ⇆ FastAPI Webhook ⇆ Meta WhatsApp Cloud API
                 ⇆ JSON data (faq.json, orders.json)
```

## ✅ Test Examples

- Send `shipping?` or `refund?` → FAQ answers
- Send `order A1B2C3` → mock order status

## 🛠 Troubleshooting

- 403 on webhook setup: Verify Token mismatch.
- 401/403 from API: Token expired.
- Template errors: Ensure approved template name.
- CORS errors: Add dashboard origin to `CORS_ORIGINS` in `.env`.

## 🗺 Roadmap

- SQLite + ORM
- Signature verification
- Agent inbox
- NLU intent classification
- Template parameter UI helpers

## 📄 License

MIT

