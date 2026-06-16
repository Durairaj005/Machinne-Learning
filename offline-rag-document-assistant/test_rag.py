import fitz
import numpy as np
from src.rag_pipeline import process_pdfs, answer_question
from src.query_classifier import classify_query

def create_mock_pdf_bytes() -> bytes:
    # Use PyMuPDF to create a simple PDF in memory
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a document about Antigravity AI, which is a powerful agentic AI coding assistant designed by Google DeepMind.")
    page.insert_text((50, 100), "Antigravity has tools for file viewing, editing, and running terminal commands.")
    page.insert_text((50, 150), "The system runs offline and does not require paid API keys.")
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def main():
    print("Creating mock PDF...")
    pdf_bytes = create_mock_pdf_bytes()
    
    payload = [
        {"file_name": "test_guide.pdf", "pdf_bytes": pdf_bytes}
    ]
    
    print("Processing PDFs through rag_pipeline...")
    # Run with default settings
    result = process_pdfs(
        uploaded_pdfs=payload,
        vector_store_dir="test_vector_store",
        chunk_size=500,
        overlap=50,
        embedding_model_name="all-MiniLM-L6-v2",
        auto_optimize=False
    )
    
    print("Successfully processed PDFs!")
    print(f"Total PDFs: {result['total_pdfs']}")
    print(f"Total Chunks: {len(result['chunks'])}")
    for i, chunk in enumerate(result['chunks']):
        print(f"Chunk {i+1}: {chunk['chunk_text']}")
        
    print("\nTesting Query Classification...")
    q1 = "What is Antigravity AI?"
    q2 = "Who created it?"
    print(f"Q: '{q1}' -> Type: {classify_query(q1)}")
    print(f"Q: '{q2}' -> Type: {classify_query(q2)}")

    print("\nTesting semantic search retrieval (without Ollama call)...")
    # To test without Ollama call, we can set a high threshold so it returns the guardrail answer,
    # or we can mock/patch generate_answer_with_ollama
    # Let's mock generate_answer_with_ollama by patching src.rag_pipeline.generate_answer_with_ollama
    import src.rag_pipeline
    original_generate = src.rag_pipeline.generate_answer_with_ollama
    src.rag_pipeline.generate_answer_with_ollama = lambda **kwargs: "Mocked Ollama Answer: Antigravity is a coding assistant."
    
    try:
        ans_res = answer_question(
            question=q1,
            index=result["index"],
            chunks=result["chunks"],
            embedding_model=result["embedding_model"],
            query_type=classify_query(q1),
            ollama_model_name="mock-model",
            top_k=2,
            min_similarity_for_answer=0.10 # low similarity threshold to trigger answer generation
        )
        print("Answer generation output:")
        print(ans_res)
    finally:
        src.rag_pipeline.generate_answer_with_ollama = original_generate

if __name__ == "__main__":
    main()
