import json
import requests
import streamlit as st

st.set_page_config(page_title="WhatsApp Bot Dashboard", layout="centered")

st.title("📲 WhatsApp FAQ & Order Bot — Dashboard")
backend_url = st.text_input("Backend Base URL", value="http://localhost:8000")

st.markdown("---")

# --- Send Template ---
st.subheader("Send Template Message")
with st.form("template_form"):
    to = st.text_input("Recipient (E.164 format)", placeholder="15551234567")
    template_name = st.text_input("Template Name (optional)")
    lang_code = st.text_input("Language Code (optional)", value="en_US")
    components_raw = st.text_area(
        "Components JSON (optional)",
        placeholder='e.g. [{"type":"body","parameters":[{"type":"text","text":"A1B2C3"}]}]'
    )
    submitted = st.form_submit_button("Send Template")

    if submitted and to:
        try:
            components = json.loads(components_raw) if components_raw.strip() else None
        except Exception as e:
            st.error(f"Invalid components JSON: {e}")
            components = None
        payload = {
            "to": to,
            "template_name": template_name or None,
            "lang_code": lang_code or None,
            "components": components,
        }
        r = requests.post(f"{backend_url}/send_template", json=payload, timeout=30)
        try:
            st.code(r.json(), language="json")
        except Exception:
            st.write(r.text)

st.markdown("---")

# --- Send Text ---
st.subheader("Send Text Message")
with st.form("text_form"):
    to2 = st.text_input("Recipient (E.164 format)", key="to2")
    text = st.text_area("Text", value="Hello from the dashboard!")
    submitted2 = st.form_submit_button("Send Text")
    if submitted2 and to2 and text:
        r = requests.post(f"{backend_url}/send_text", json={"to": to2, "text": text}, timeout=30)
        try:
            st.code(r.json(), language="json")
        except Exception:
            st.write(r.text)

st.markdown("---")

# --- FAQ Tester ---
st.subheader("Test FAQ Locally (no WhatsApp)")
q = st.text_input("Ask a question (e.g., 'What about shipping?')")
if st.button("Test FAQ") and q:
    try:
        faq = requests.get(f"{backend_url}/admin/faq", timeout=30).json()
        ans = None
        ql = q.lower()
        for item in faq.get("items", []):
            for kw in item.get("keywords", []):
                if kw.lower() in ql:
                    ans = item.get("answer")
                    break
            if ans:
                break
        st.success(ans or "No FAQ match. Try editing FAQ keywords below.")
    except Exception as e:
        st.error(f"Failed to fetch FAQ: {e}")

st.markdown("---")

# --- Order Tester ---
st.subheader("Test Order Lookup Locally")
try:
    orders = requests.get(f"{backend_url}/admin/orders", timeout=30).json()
except Exception as e:
    orders = {}
    st.error(f"Failed to load orders: {e}")

order_id = st.text_input("Order ID (e.g., A1B2C3)")
if st.button("Lookup Order") and order_id:
    info = orders.get("orders", {}).get(order_id)
    if info:
        st.json({"order_id": order_id, **info})
    else:
        st.warning("Order not found.")

st.markdown("---")

# --- FAQ Admin ---
st.subheader("View / Edit FAQ JSON")
try:
    faq_json = requests.get(f"{backend_url}/admin/faq", timeout=30).json()
except Exception as e:
    faq_json = {"items": []}
    st.error(f"Failed to load FAQ: {e}")

new_faq = st.text_area("FAQ JSON", value=json.dumps(faq_json, ensure_ascii=False, indent=2), height=300)
if st.button("Save FAQ"):
    try:
        parsed = json.loads(new_faq)
        r = requests.put(f"{backend_url}/admin/faq", json=parsed, timeout=30)
        if r.ok:
            st.success("Saved!")
        else:
            st.error(r.text)
    except Exception as e:
        st.error(f"Invalid JSON: {e}")

st.info("Tip: Keep keywords broad (e.g., 'shipping', 'refund', 'price') for reliable matches.")
