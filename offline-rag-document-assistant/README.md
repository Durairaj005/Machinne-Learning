# Offline RAG-Based AI Document Assistant Using Open-Source LLM and Vector Database

## Objective
Build a fully offline AI-powered document assistant that can answer questions from uploaded PDF files using a Retrieval-Augmented Generation (RAG) pipeline.

## Interview Summary
This project is a fully offline RAG-based AI document assistant. It uses open-source embeddings and a FAISS vector database to retrieve relevant content from uploaded PDFs. A local open-source LLM running through Ollama generates answers from the retrieved context. Since the project does not use any paid API key, it is cost-free and suitable for secure document analysis.

This enhanced project is not just a simple PDF chatbot. It is a complete offline RAG-based document intelligence system. It supports multiple PDFs, retrieves relevant chunks using FAISS vector search, tracks sources with file name and page number, classifies user queries, generates answers using a local Ollama LLM, and evaluates performance using similarity score, response time, chunk count, and confidence level.

## Features
- Upload multiple PDF documents from a Streamlit dashboard
- Extract text using PyMuPDF
- Split text into overlapping chunks with metadata
- Generate embeddings with SentenceTransformers (`all-MiniLM-L6-v2`)
- Store and search vectors using FAISS
- Ask natural-language questions about the uploaded document
- Retrieve top relevant chunks with similarity scores
- Generate answers using a local Ollama model (for example `llama3.2`, `mistral`, `phi3`)
- Track sources with file name, page number, and chunk number
- Classify questions into definition, summary, comparison, direct fact, or unknown type
- Show evaluation metrics:
  - Total PDFs uploaded
  - Number of chunks created
  - Top similarity scores
  - Average similarity score
  - Response time
  - Confidence level
- Display retrieved source chunks for transparency
- Runs fully offline and uses no paid API keys (free and open-source setup)

## Tech Stack
- Python
- Streamlit
- PyMuPDF
- SentenceTransformers
- FAISS (CPU)
- Ollama (local LLM runtime)
- NumPy
- Pandas
- Requests

## Project Structure
```text
offline-rag-document-assistant/
|
|-- app.py
|-- requirements.txt
|-- README.md
|-- sample_docs/
|-- vector_store/
|-- src/
|   |-- pdf_reader.py
|   |-- text_splitter.py
|   |-- embeddings.py
|   |-- vector_db.py
|   |-- rag_pipeline.py
|   |-- ollama_llm.py
|   |-- query_classifier.py
|
|-- assets/
```

## Installation Steps
1. Clone or download this project.
2. Open terminal in the project folder.
3. Create and activate a virtual environment.

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Install Ollama
1. Download Ollama from the official website:
   - https://ollama.com/download
2. Install it on your system.
3. Start Ollama (it usually runs as a local service).

## Pull a Local Model
Run:
```bash
ollama pull llama3.2
```

You can also use other open-source models such as `mistral` or `phi3`.

## Run the Project
```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Workflow Explanation
1. User uploads one or more PDFs in the Streamlit app.
2. Text is extracted page-by-page using PyMuPDF.
3. Extracted text is split into overlapping chunks with metadata (file name, page, chunk id).
4. Each chunk is converted to embeddings via SentenceTransformers.
5. Embeddings are indexed in FAISS for similarity search.
6. User asks a question and the query type is classified.
7. Question embedding is created.
8. Top relevant chunks are retrieved from FAISS.
9. Retrieved context, question, and query type are sent to Ollama local LLM.
10. Model answer, source chunks, and evaluation metrics (including confidence level) are displayed.

## Advantages
- Fully offline and private
- No paid API key required
- Cost-free for experimentation and learning
- Supports multiple PDFs in one searchable session
- Provides transparent source tracking with page-aware chunk references
- Includes interview-ready evaluation dashboard and confidence reporting
- Easy to extend with better chunking, reranking, and memory
- Good foundation for secure internal document Q&A tools

## Future Enhancements
- Support multiple PDF uploads and document merging
- Add OCR for scanned PDFs
- Add chat history memory across questions
- Add reranking for better retrieval precision
- Add citation highlighting by page number
- Add export of Q&A sessions

## Notes
- If Ollama is not running, the app shows a user-friendly error.
- The default embedding model is `all-MiniLM-L6-v2`.
- The Ollama model name can be changed in the Streamlit sidebar without code changes.
