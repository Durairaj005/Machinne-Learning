import os
import streamlit as st
from llama_cpp import Llama

REPO_ID = "msdrajan/llama-3.2-3b-routing-gguf"

# Replace with exact .gguf file name if "*.gguf" is slow or gives error
MODEL_FILE = "*.gguf"

LABELS = ["SALES_TEAM", "SUPPORT_TEAM", "TECH_TEAM"]

st.set_page_config(
    page_title="Fast Ticket Routing Demo",
    page_icon="🎫",
    layout="centered"
)

st.title("🎫 Fast Ticket Routing Demo")
st.write("This version loads the GGUF model only when needed and caches it after first use.")

@st.cache_resource(show_spinner=False)
def load_model():
    return Llama.from_pretrained(
        repo_id=REPO_ID,
        filename=MODEL_FILE,
        n_ctx=512,                         # smaller context = faster load/inference
        n_threads=max(2, os.cpu_count() or 4),
        n_batch=128,
        verbose=False
    )

def classify_ticket(ticket):
    prompt = f"""Classify this customer ticket into only one label.

Labels:
SALES_TEAM
SUPPORT_TEAM
TECH_TEAM

Ticket: {ticket}

Answer only the label:"""

    llm = load_model()

    response = llm(
        prompt,
        max_tokens=8,
        temperature=0,
        stop=["\n"]
    )

    output = response["choices"][0]["text"].strip().upper()

    for label in LABELS:
        if label in output:
            return label, output

    # fallback if model gives unclear answer
    text = ticket.lower()
    if any(w in text for w in ["price", "pricing", "plan", "demo", "quote", "quotation", "discount", "buy", "purchase"]):
        return "SALES_TEAM", output
    if any(w in text for w in ["payment", "refund", "billing", "invoice", "login", "password", "account", "subscription"]):
        return "SUPPORT_TEAM", output
    return "TECH_TEAM", output

samples = [
    "I want to know the pricing for enterprise plan",
    "My payment went through but subscription is not active",
    "API responses are very slow",
    "I forgot my password and cannot login",
    "Can I get a quotation for 50 users",
    "The application crashes when I upload a file"
]

sample = st.selectbox("Sample ticket", [""] + samples)

ticket = st.text_area(
    "Enter customer ticket",
    value=sample,
    height=120,
    placeholder="Example: I am getting a 500 error from the backend"
)

st.caption("Note: First prediction may take time because the model loads. After that, it is cached and faster.")

if st.button("Route Ticket"):
    if not ticket.strip():
        st.warning("Please enter a ticket.")
    else:
        with st.spinner("Loading model and routing ticket... First time may take some time."):
            label, raw = classify_ticket(ticket)

        st.success(f"Assigned Team: {label}")

        if label == "SALES_TEAM":
            st.info("Sales team handles pricing, plans, demos, quotations, and purchases.")
        elif label == "SUPPORT_TEAM":
            st.info("Support team handles login, account, billing, refund, and subscription issues.")
        else:
            st.info("Tech team handles API, bugs, crashes, backend errors, integrations, and performance issues.")

        with st.expander("Raw model output"):
            st.write(raw)

st.markdown("---")
st.caption("Built using Streamlit + llama-cpp-python + Hugging Face GGUF")