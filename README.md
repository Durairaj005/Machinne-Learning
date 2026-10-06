# Machine Learning & AI Projects Repository

Welcome to the Machine Learning and AI projects workspace. This repository hosts individual self-contained projects.

---

## 📂 Projects Directory

### 🧠 1. [Digit Recognition AI](./digit-recognition-ai)
A full-stack project utilizing a deep learning backend (Python / FastAPI / TensorFlow CNN) and an interactive frontend canvas (React / Vite / Tailwind CSS) to recognize handwritten digits (0–9) in real-time from drawings and camera photos with 98.78% accuracy.
* **Backend**: FastAPI, TensorFlow/Keras CNN, OpenCV adaptive document preprocessor.
* **Frontend**: Responsive drawing canvas, image upload studio, live confidence gauge, and Recharts/matrix analytics.

### 📄 2. [Offline RAG AI Document Assistant](./offline-rag-document-assistant)
A fully offline RAG (Retrieval-Augmented Generation) document intelligence chat application. It extracts text from uploaded PDFs, chunks it, stores embeddings in a FAISS vector database, and queries a local open-source LLM (such as Llama 3.2 via Ollama) to answer questions based entirely on document context.
* **Core**: Python, Streamlit, PyMuPDF, SentenceTransformers (`all-MiniLM-L6-v2`), FAISS, Ollama.
* **Features**: Automated chunk-tuning, confidence scoring, citation source expansion, and glassmorphism design.

---

## ⚡ Running the Projects

Each project has its own folder containing a dedicated configuration, requirements list, and guides.
* For the Digit Recognition AI: Navigate to `./digit-recognition-ai` and consult [`digit-recognition-ai/README.md`](./digit-recognition-ai/README.md).
* For the Document Assistant, you can use the launcher script [`run.bat`](./run.bat) at the workspace root.
