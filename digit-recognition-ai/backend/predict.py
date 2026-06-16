from functools import lru_cache
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from tensorflow.keras.models import load_model


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = BASE_DIR / "model" / "digit_model.h5"


def _read_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Decode an uploaded JPG/PNG byte stream into a grayscale image."""
    np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Unable to decode the uploaded image.")
    return image


def _read_image_path(image_path: Path) -> np.ndarray:
    """Read an image from disk in grayscale format."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Unable to read image at {image_path}.")
    return image


def preprocess_image(
    image_bytes: Optional[bytes] = None,
    image_path: Optional[Path] = None,
) -> np.ndarray:
    """Convert an input image to the CNN-ready 28x28 normalized tensor."""
    if image_bytes is None and image_path is None:
        raise ValueError("Provide image_bytes or image_path.")

    if image_bytes is not None:
        image = _read_image_bytes(image_bytes)
    else:
        image = _read_image_path(Path(image_path))

    image = cv2.resize(image, (28, 28), interpolation=cv2.INTER_AREA)

    # Light backgrounds are inverted so the model receives a digit-centric image.
    if image.mean() > 127:
        image = 255 - image

    image = image.astype("float32") / 255.0
    image = np.expand_dims(image, axis=-1)
    image = np.expand_dims(image, axis=0)
    return image


@lru_cache(maxsize=1)
def get_model(model_path: str = str(DEFAULT_MODEL_PATH)):
    """Load the trained Keras model once and reuse it across requests."""
    resolved_path = Path(model_path)
    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Model file not found at {resolved_path}. Train the model first."
        )
    return load_model(resolved_path)


def predict_digit(
    image_bytes: Optional[bytes] = None,
    image_path: Optional[Path] = None,
    model_path: str = str(DEFAULT_MODEL_PATH),
):
    """Run inference and return the predicted digit plus class probabilities."""
    model = get_model(model_path)
    tensor = preprocess_image(image_bytes=image_bytes, image_path=image_path)
    probabilities = model.predict(tensor, verbose=0)[0]
    digit = int(np.argmax(probabilities))
    confidence = float(np.max(probabilities))

    return {
        "digit": digit,
        "confidence": confidence,
        "probabilities": [float(value) for value in probabilities],
    }