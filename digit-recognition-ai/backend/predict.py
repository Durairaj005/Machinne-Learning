from functools import lru_cache
from pathlib import Path
from typing import Optional

import sys
import urllib.request
import cv2
import numpy as np

try:
    import six
    sys.modules["six.moves.urllib"] = urllib
    sys.modules["six.moves.urllib.request"] = urllib.request
    six.moves.urllib = urllib
    six.moves.urllib.request = urllib.request
except Exception:
    pass

try:
    from tensorflow.keras.models import load_model
except Exception:
    from keras.models import load_model


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
    """Convert input image (canvas drawing or paper camera photo) to CNN-ready 28x28 normalized tensor."""
    if image_bytes is None and image_path is None:
        raise ValueError("Provide image_bytes or image_path.")

    if image_bytes is not None:
        image = _read_image_bytes(image_bytes)
    else:
        image = _read_image_path(Path(image_path))

    h, w = image.shape

    # Determine if background is predominantly light (e.g. paper or white canvas)
    border_pixels = np.concatenate([image[0, :], image[-1, :], image[:, 0], image[:, -1]])
    is_light_bg = float(np.median(border_pixels)) > 115 or float(image.mean()) > 127

    # Smooth image to suppress paper grain / camera sensor noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    if is_light_bg:
        # Use adaptive threshold to handle non-uniform paper shadows, desk borders, and lighting variations
        block_size = max(15, (min(h, w) // 25) | 1)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, block_size, 10
        )
    else:
        # Dark background (e.g. standard MNIST or dark canvas)
        _, binary = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find candidate digit contours (using RETR_LIST to capture strokes inside paper/document cards)
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    valid_boxes = []
    margin = max(4, int(min(h, w) * 0.01))
    total_image_area = float(h * w)

    for c in contours:
        bx, by, bw, bh = cv2.boundingRect(c)
        area = cv2.contourArea(c)

        # Ignore outer image borders or page edges
        if bx <= margin or by <= margin or (bx + bw) >= w - margin or (by + bh) >= h - margin:
            continue
        # Ignore card/page boundaries: area > 12% of total image or dimensions > 60% of total image
        if area > total_image_area * 0.12 or bw > w * 0.60 or bh > h * 0.60:
            continue
        # Ignore tiny speckles
        if area < 30 and (bw * bh) < 60:
            continue

        valid_boxes.append((bx, by, bw, bh, area))

    if valid_boxes:
        valid_boxes.sort(key=lambda b: b[4], reverse=True)
        max_area = valid_boxes[0][4]
        # Include main digit stroke and any nearby component strokes
        digit_boxes = [b for b in valid_boxes if b[4] >= max_area * 0.05 or b[4] > 80]
        min_x = min(b[0] for b in digit_boxes)
        min_y = min(b[1] for b in digit_boxes)
        max_x = max(b[0] + b[2] for b in digit_boxes)
        max_y = max(b[1] + b[3] for b in digit_boxes)

        pad = max(4, int(min(max_x - min_x, max_y - min_y) * 0.08))
        cx1, cy1 = max(0, min_x - pad), max(0, min_y - pad)
        cx2, cy2 = min(w, max_x + pad), min(h, max_y + pad)

        digit_crop = binary[cy1:cy2, cx1:cx2]
    else:
        # Fallback to binary image directly
        digit_crop = binary

    ch, cw = digit_crop.shape

    # Fit into 20x20 bounding box maintaining aspect ratio (MNIST standard)
    if cw > ch:
        nw = 20
        nh = max(1, int(round(ch * 20.0 / cw)))
    else:
        nh = 20
        nw = max(1, int(round(cw * 20.0 / ch)))

    resized = cv2.resize(digit_crop, (nw, nh), interpolation=cv2.INTER_AREA)

    # Dilate slightly if stroke is very thin to match MNIST stroke density
    if (resized > 40).sum() < 45:
        resized = cv2.dilate(resized, np.ones((2, 2), np.uint8))

    # Pad into 28x28 frame
    padded = np.zeros((28, 28), dtype=np.float32)
    sy = (28 - nh) // 2
    sx = (28 - nw) // 2
    padded[sy : sy + nh, sx : sx + nw] = resized

    # Center by center of mass (MNIST dataset specification)
    try:
        from scipy import ndimage
        cy, cx = ndimage.center_of_mass(padded)
        if not np.isnan(cy) and not np.isnan(cx):
            shift_y = 14.0 - cy
            shift_x = 14.0 - cx
            M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            padded = cv2.warpAffine(padded, M, (28, 28), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    except Exception:
        pass

    tensor = (padded / 255.0).astype(np.float32)
    tensor = np.expand_dims(tensor, axis=-1)
    tensor = np.expand_dims(tensor, axis=0)
    return tensor


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