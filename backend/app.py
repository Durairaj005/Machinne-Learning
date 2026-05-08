from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

try:
    # Preferred: package-relative import when running as `backend.app`
    from .predict import DEFAULT_MODEL_PATH, predict_digit
except Exception:  # pragma: no cover - allow running the module directly
    # Fallback for running from the `backend` folder (e.g., `python -m uvicorn app:app`)
    from predict import DEFAULT_MODEL_PATH, predict_digit


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
HISTORY_PATH = MODEL_DIR / "history.json"
CURVE_PATH = MODEL_DIR / "training_curves.png"
CONFUSION_MATRIX_PATH = MODEL_DIR / "confusion_matrix.png"
SAMPLE_PREDICTIONS_PATH = MODEL_DIR / "sample_predictions.png"


app = FastAPI(title="AI Handwritten Digit Recognition API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if MODEL_DIR.exists():
    app.mount("/artifacts", StaticFiles(directory=MODEL_DIR), name="artifacts")


def load_history() -> Dict[str, Any]:
    """Load the metrics file saved by the training script."""
    if not HISTORY_PATH.exists():
        return {
            "accuracy": [],
            "val_accuracy": [],
            "loss": [],
            "val_loss": [],
        }

    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


@app.get("/health")
def health():
    """Basic health check plus model availability status."""
    return {
        "status": "ok",
        "model_ready": DEFAULT_MODEL_PATH.exists(),
    }


@app.get("/metrics")
def metrics():
    """Expose training metrics and artifact URLs to the frontend."""
    history = load_history()
    return {
        "history": history,
        "artifacts": {
            "training_curves": "/artifacts/training_curves.png" if CURVE_PATH.exists() else None,
            "confusion_matrix": "/artifacts/confusion_matrix.png" if CONFUSION_MATRIX_PATH.exists() else None,
            "sample_predictions": "/artifacts/sample_predictions.png" if SAMPLE_PREDICTIONS_PATH.exists() else None,
        },
        "model_exists": DEFAULT_MODEL_PATH.exists(),
    }


@app.get("/sample-predictions")
def sample_predictions():
    """Return the sample-prediction gallery if it has been generated."""
    if not SAMPLE_PREDICTIONS_PATH.exists():
        raise HTTPException(status_code=404, detail="Sample predictions are not available yet.")
    return FileResponse(SAMPLE_PREDICTIONS_PATH)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Accept an uploaded JPG image and return a digit prediction."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    if not DEFAULT_MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail="Model is not trained yet.")

    try:
        image_bytes = await file.read()
        result = predict_digit(image_bytes=image_bytes)
        probabilities = result["probabilities"]
        top_indices = sorted(range(len(probabilities)), key=lambda idx: probabilities[idx], reverse=True)[:3]

        return JSONResponse(
            {
                "predicted_digit": result["digit"],
                "confidence": round(result["confidence"] * 100, 2),
                "probabilities": probabilities,
                "top_predictions": [
                    {"digit": int(index), "probability": round(probabilities[index] * 100, 2)}
                    for index in top_indices
                ],
                "filename": file.filename,
            }
        )
    except Exception as exc:  # pragma: no cover - user-facing guardrail
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/")
def root():
    """Simple landing response for local backend checks."""
    return {"message": "AI Handwritten Digit Recognition API"}