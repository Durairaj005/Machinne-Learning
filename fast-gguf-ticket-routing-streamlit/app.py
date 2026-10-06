import os
import streamlit as st
from llama_cpp import Llama

REPO_ID = "msdrajan/llama-3.2-3b-routing-gguf"
MODEL_FILE = "Llama-3.2-3B-Instruct.Q4_K_M.gguf"
LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", MODEL_FILE)

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
    if os.path.exists(LOCAL_MODEL_PATH):
        model_path = LOCAL_MODEL_PATH
    else:
        from huggingface_hub import hf_hub_download
        model_path = hf_hub_download(repo_id=REPO_ID, filename=MODEL_FILE)

    return Llama(
        model_path=model_path,
        n_ctx=512,                         # smaller context = faster load/inference
        n_threads=max(2, os.cpu_count() or 4),
        n_batch=128,
        verbose=False
    )

def rule_based_fallback(ticket):
    text = ticket.lower()
    if any(w in text for w in ["price", "pricing", "plan", "demo", "quote", "quotation", "discount", "buy", "purchase"]):
        return "SALES_TEAM"
    if any(w in text for w in ["payment", "refund", "billing", "invoice", "login", "password", "account", "subscription"]):
        return "SUPPORT_TEAM"
    return "TECH_TEAM"

def classify_ticket(ticket):
    try:
        llm = load_model()
        prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n\n"
            f"You are a ticket classification assistant. Classify the customer ticket into exactly one category: "
            f"SALES_TEAM, SUPPORT_TEAM, or TECH_TEAM. Respond with ONLY the label.<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"Ticket: {ticket}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        response = llm(
            prompt,
            max_tokens=8,
            temperature=0,
            stop=["<|eot_id|>", "\n"]
        )
        output = response["choices"][0]["text"].strip().upper()
        for label in LABELS:
            if label in output:
                return label, output
        fallback_label = rule_based_fallback(ticket)
        return fallback_label, f"{output} (fallback applied: {fallback_label})"
    except Exception as e:
        fallback_label = rule_based_fallback(ticket)
        return fallback_label, f"Model unavailable ({e}). Fallback applied: {fallback_label}"

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

st.caption("Note: First prediction may take a few seconds as the model loads into memory. Subsequent predictions are cached and fast.")

if st.button("Route Ticket"):
    if not ticket.strip():
        st.warning("Please enter a ticket.")
    else:
        with st.spinner("Routing ticket..."):
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