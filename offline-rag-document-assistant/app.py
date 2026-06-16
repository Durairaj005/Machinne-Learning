import os
import sys

# Silence progress bars
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "1"

# Safe stream wrapper to prevent Windows OS errors on redirected stdout/stderr
class SafeStream:
    def __init__(self, original_stream):
        self.original_stream = original_stream

    def write(self, data):
        try:
            if self.original_stream:
                self.original_stream.write(data)
        except Exception:
            pass

    def flush(self):
        try:
            if self.original_stream:
                self.original_stream.flush()
        except Exception:
            pass

    def isatty(self):
        try:
            return self.original_stream.isatty() if self.original_stream else False
        except Exception:
            return False

sys.stderr = SafeStream(sys.stderr)
sys.stdout = SafeStream(sys.stdout)

import numpy as np
import pandas as pd
import streamlit as st

from src.auto_tuner import recommend_chunk_settings, recommend_retrieval_settings
from src.query_classifier import classify_query
from src.rag_pipeline import answer_question, process_pdfs


st.set_page_config(
    page_title="Offline RAG-Based AI Document Assistant",
    page_icon="📄",
    layout="wide",
)


def init_session_state() -> None:
    defaults = {
        "index": None,
        "chunks": [],
        "embedding_model": None,
        "pdf_names": [],
        "pdf_count": 0,
        "chunk_count": 0,
        "is_processed": False,
        "auto_optimize": True,
        "active_chunk_size": 500,
        "active_overlap": 50,
        "active_top_k": 3,
        "active_min_similarity": 0.45,
        "file_settings": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> tuple[str, bool, int, float, int, int]:
    st.sidebar.title("Settings")
    ollama_model = st.sidebar.text_input(
        "Ollama model name",
        value="llama3.2",
        help="Examples: llama3.2, mistral, phi3",
    )
    auto_optimize = st.sidebar.checkbox(
        "Auto-optimize settings based on input",
        value=True,
        help="Automatically tune chunking and retrieval for better efficiency.",
    )

    top_k = st.sidebar.slider(
        "Top-K chunks",
        min_value=1,
        max_value=8,
        value=3,
        disabled=auto_optimize,
    )
    min_similarity = st.sidebar.slider(
        "Minimum similarity for answer",
        min_value=0.20,
        max_value=0.80,
        value=0.45,
        step=0.01,
        disabled=auto_optimize,
    )
    chunk_size = st.sidebar.slider(
        "Chunk size (words)",
        min_value=200,
        max_value=800,
        value=500,
        step=50,
        disabled=auto_optimize,
    )
    overlap = st.sidebar.slider(
        "Chunk overlap (words)",
        min_value=20,
        max_value=200,
        value=50,
        step=10,
        disabled=auto_optimize,
    )

    if auto_optimize:
        st.sidebar.caption("Auto mode enabled: the app will choose chunking and retrieval settings.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Instructions")
    st.sidebar.write("1. Upload one or more PDF documents.")
    st.sidebar.write("2. Click 'Process PDFs' to build the vector index.")
    st.sidebar.write("3. Ask a question related to the document.")
    st.sidebar.write("4. Review answer, scores, and source chunks.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Runs fully offline with local Ollama + open-source libraries.")
    return ollama_model, auto_optimize, top_k, min_similarity, chunk_size, overlap


def process_uploaded_pdfs(uploaded_files, auto_optimize: bool, chunk_size: int, overlap: int) -> None:
    payload = []
    total_bytes = 0
    for file in uploaded_files:
        file_bytes = file.getvalue()
        payload.append({"file_name": file.name, "pdf_bytes": file_bytes})
        total_bytes += len(file_bytes)

    selected_chunk_size = chunk_size
    selected_overlap = overlap
    if auto_optimize:
        selected_chunk_size, selected_overlap = recommend_chunk_settings(
            total_pdfs=len(uploaded_files),
            total_bytes=total_bytes,
        )

    with st.spinner("Reading PDFs, creating chunks, generating embeddings, and building FAISS index..."):
        result = process_pdfs(
            uploaded_pdfs=payload,
            vector_store_dir="vector_store",
            chunk_size=selected_chunk_size,
            overlap=selected_overlap,
            embedding_model_name="all-MiniLM-L6-v2",
            auto_optimize=auto_optimize,
        )

    st.session_state.index = result["index"]
    st.session_state.chunks = result["chunks"]
    st.session_state.embedding_model = result["embedding_model"]
    st.session_state.pdf_names = [file.name for file in uploaded_files]
    st.session_state.pdf_count = result["total_pdfs"]
    st.session_state.chunk_count = len(result["chunks"])
    st.session_state.auto_optimize = auto_optimize
    st.session_state.active_chunk_size = selected_chunk_size
    st.session_state.active_overlap = selected_overlap
    st.session_state.file_settings = result.get("file_settings", [])
    st.session_state.is_processed = True


def display_retrieval_table(retrieved_chunks):
    if not retrieved_chunks:
        st.info("No chunks were retrieved.")
        return

    table_rows = []
    for item in retrieved_chunks:
        preview = item["chunk_text"][:200].replace("\n", " ")
        if len(item["chunk_text"]) > 200:
            preview += "..."

        table_rows.append(
            {
                "File Name": item["file_name"],
                "Page Number": item["page_number"],
                "Chunk Number": item["chunk_id"],
                "Similarity Score": np.round(item["score"], 4),
                "Preview": preview,
            }
        )

    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)


def load_css(file_path: str):
    import os
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main() -> None:
    init_session_state()
    load_css("assets/style.css")

    st.title("Offline RAG-Based AI Document Assistant Using Open-Source LLM and Vector Database")
    st.write(
        "Upload a PDF, ask questions, and get answers generated by a local Ollama model "
        "using retrieval-augmented generation (RAG)."
    )

    ollama_model, auto_optimize, top_k, min_similarity, chunk_size, overlap = render_sidebar()

    st.subheader("PDF Upload Area")
    uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        if uploaded_files:
            st.success(f"Selected PDFs: {len(uploaded_files)}")
            for file in uploaded_files:
                st.write(f"- {file.name}")

            if st.button("Process PDFs", type="primary", use_container_width=True):
                try:
                    process_uploaded_pdfs(uploaded_files, auto_optimize, chunk_size, overlap)
                    st.success("PDFs processed successfully. You can now ask questions.")
                    st.info(
                        f"Active chunk settings -> Chunk Size: {st.session_state.active_chunk_size}, "
                        f"Overlap: {st.session_state.active_overlap}"
                    )
                    if st.session_state.file_settings:
                        st.caption("Per-file word-aware tuning:")
                        for file_info in st.session_state.file_settings:
                            st.write(
                                f"- {file_info['file_name']} | Words: {file_info['word_count']} | "
                                f"Pages: {file_info['page_count']} | Chunk Size: {file_info['chunk_size']} | "
                                f"Overlap: {file_info['overlap']}"
                            )
                except Exception as exc:
                    import traceback
                    tb_str = traceback.format_exc()
                    st.error(f"Failed to process PDFs: {exc}")
                    with st.expander("Show detailed error log"):
                        st.code(tb_str)
        else:
            st.info("Please upload one or more PDF files to begin.")

    with col_right:
        st.subheader("Question Input Area")
        question = st.text_input("Enter your question")
        query_type = classify_query(question)
        st.write(f"Query Type: {query_type}")

        ask_button = st.button("Generate Answer", use_container_width=True)
        if ask_button:
            if not st.session_state.is_processed:
                st.warning("Please upload and process PDF files before asking questions.")
            elif not question.strip():
                st.warning("Please enter a question.")
            else:
                try:
                    effective_top_k = top_k
                    effective_min_similarity = min_similarity
                    if auto_optimize:
                        effective_top_k, effective_min_similarity = recommend_retrieval_settings(
                            question=question,
                            query_type=query_type,
                            total_chunks=st.session_state.chunk_count,
                        )

                    st.session_state.active_top_k = effective_top_k
                    st.session_state.active_min_similarity = effective_min_similarity

                    with st.spinner("Retrieving relevant chunks and querying Ollama..."):
                        result = answer_question(
                            question=question,
                            index=st.session_state.index,
                            chunks=st.session_state.chunks,
                            embedding_model=st.session_state.embedding_model,
                            query_type=query_type,
                            ollama_model_name=ollama_model,
                            top_k=effective_top_k,
                            min_similarity_for_answer=effective_min_similarity,
                        )

                    st.subheader("AI Answer Section")
                    st.markdown(
                        f'<div class="premium-card"><p style="margin:0; font-size:1.05rem; line-height:1.6; color:#f1f5f9;">{result["answer"]}</p></div>',
                        unsafe_allow_html=True
                    )

                    retrieved_chunks = result["retrieved_chunks"]
                    top_scores = [np.round(score, 4) for score in result["top_similarity_scores"]]

                    st.subheader("Evaluation Metrics Section")
                    scores_str = ", ".join(map(str, top_scores)) if top_scores else "N/A"
                    metrics_html = f"""
                    <div class="metrics-container">
                        <div class="metric-badge info-border">
                            <div class="metric-label">Total PDFs Uploaded</div>
                            <div class="metric-value">{st.session_state.pdf_count}</div>
                        </div>
                        <div class="metric-badge info-border">
                            <div class="metric-label">Total Text Chunks</div>
                            <div class="metric-value">{st.session_state.chunk_count}</div>
                        </div>
                        <div class="metric-badge info-border">
                            <div class="metric-label">Top Similarity Scores</div>
                            <div class="metric-value">{scores_str}</div>
                        </div>
                        <div class="metric-badge success-border">
                            <div class="metric-label">Average Similarity Score</div>
                            <div class="metric-value">{result['average_similarity_score']:.4f}</div>
                        </div>
                        <div class="metric-badge warning-border">
                            <div class="metric-label">Response Time</div>
                            <div class="metric-value">{result['response_time']:.2f}s</div>
                        </div>
                        <div class="metric-badge success-border">
                            <div class="metric-label">Confidence Level</div>
                            <div class="metric-value">{result['confidence_level']}</div>
                        </div>
                    </div>
                    """
                    st.markdown(metrics_html, unsafe_allow_html=True)

                    st.caption(
                        f"Active Retrieval Settings -> Top-K: {st.session_state.active_top_k}, "
                        f"Min Similarity: {st.session_state.active_min_similarity:.2f}"
                    )

                    st.subheader("Retrieved Source Chunks Section")
                    display_retrieval_table(retrieved_chunks)

                    for rank, item in enumerate(retrieved_chunks, start=1):
                        source_line = (
                            f"Source: {item['file_name']} | Page: {item['page_number']} | Chunk: {item['chunk_id']}"
                        )
                        with st.expander(f"{source_line} | Score: {item['score']:.4f}"):
                            st.write(source_line)
                            st.write(item["chunk_text"])
                except Exception as exc:
                    st.error(f"Could not generate an answer: {exc}")

    st.markdown("---")
    st.caption(
        "Tech Stack: Python, Streamlit, PyMuPDF, SentenceTransformers, FAISS, Ollama, Pandas, NumPy. "
        "No paid API keys required."
    )


if __name__ == "__main__":
    main()
