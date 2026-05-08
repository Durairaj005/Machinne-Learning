from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
DEFAULT_TRAIN_CSV = WORKSPACE_ROOT / "mnist_train.csv"
DEFAULT_TEST_CSV = WORKSPACE_ROOT / "mnist_test.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "digit_model.h5"
HISTORY_PATH = MODEL_DIR / "history.json"
CURVE_PATH = MODEL_DIR / "training_curves.png"
CONFUSION_MATRIX_PATH = MODEL_DIR / "confusion_matrix.png"
SAMPLE_PREDICTIONS_PATH = MODEL_DIR / "sample_predictions.png"


def load_csv_dataset(csv_path: Path, has_labels: bool = True, max_rows: int | None = None):
    """Load MNIST rows from a CSV file and reshape them into CNN tensors."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    data_frame = pd.read_csv(csv_path, low_memory=False, nrows=max_rows)
    data_frame = data_frame.apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)

    if has_labels:
        if "label" not in data_frame.columns:
            raise ValueError(f"Expected a label column in {csv_path}")
        y = data_frame["label"].astype(np.int32).to_numpy()
        x = data_frame.drop(columns=["label"]).to_numpy(dtype=np.float32)
    else:
        y = None
        x = data_frame.to_numpy(dtype=np.float32)

    if x.shape[1] != 784:
        raise ValueError(
            f"Expected 784 pixel columns in {csv_path}, but found {x.shape[1]}."
        )

    x = x / 255.0
    x = x.reshape(-1, 28, 28, 1)
    return x, y


def build_model():
    """Create a compact CNN suitable for handwritten digit recognition."""
    model = Sequential(
        [
            Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1)),
            Conv2D(32, (3, 3), activation="relu"),
            MaxPooling2D((2, 2)),
            Dropout(0.25),
            Conv2D(64, (3, 3), activation="relu"),
            MaxPooling2D((2, 2)),
            Dropout(0.25),
            Conv2D(128, (3, 3), activation="relu"),
            Flatten(),
            Dense(256, activation="relu"),
            Dropout(0.5),
            Dense(10, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def save_history(history):
    """Persist training metrics for the frontend dashboard."""
    data = {key: [float(value) for value in values] for key, values in history.history.items()}
    HISTORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def save_training_curves(history):
    """Plot accuracy and loss curves from the training run."""
    epochs = range(1, len(history.history["accuracy"]) + 1)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, history.history["accuracy"], label="Training Accuracy", linewidth=2)
    plt.plot(epochs, history.history["val_accuracy"], label="Validation Accuracy", linewidth=2)
    plt.title("Model Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(alpha=0.2)

    plt.subplot(1, 2, 2)
    plt.plot(epochs, history.history["loss"], label="Training Loss", linewidth=2)
    plt.plot(epochs, history.history["val_loss"], label="Validation Loss", linewidth=2)
    plt.title("Model Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(CURVE_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def save_confusion_matrix_plot(y_true, y_pred):
    """Render a confusion matrix heatmap for the test split."""
    matrix = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(8, 7))
    plt.imshow(matrix, interpolation="nearest", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.colorbar()
    tick_marks = np.arange(10)
    plt.xticks(tick_marks, tick_marks)
    plt.yticks(tick_marks, tick_marks)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            plt.text(col, row, matrix[row, col], ha="center", va="center", color="black")

    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def save_sample_predictions(model, x_test, y_test):
    """Create a visual gallery of correct and incorrect predictions."""
    predictions = model.predict(x_test[:12], verbose=0)
    predicted_labels = np.argmax(predictions, axis=1)

    plt.figure(figsize=(14, 8))
    for index in range(12):
        plt.subplot(3, 4, index + 1)
        plt.imshow(x_test[index].squeeze(), cmap="gray")
        plt.axis("off")
        plt.title(f"Pred: {predicted_labels[index]} | True: {y_test[index]}")

    plt.tight_layout()
    plt.savefig(SAMPLE_PREDICTIONS_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def train(
    train_csv: Path,
    test_csv: Path,
    epochs: int,
    batch_size: int,
    max_train_rows: int | None = None,
    max_test_rows: int | None = None,
):
    """Train the CNN and export the model plus dashboard artifacts."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    x_train_full, y_train_full = load_csv_dataset(train_csv, has_labels=True, max_rows=max_train_rows)
    x_test, y_test = load_csv_dataset(test_csv, has_labels=True, max_rows=max_test_rows)

    x_train, x_val, y_train, y_val = train_test_split(
        x_train_full,
        y_train_full,
        test_size=0.15,
        random_state=42,
        stratify=y_train_full,
    )

    y_train_encoded = to_categorical(y_train, num_classes=10)
    y_val_encoded = to_categorical(y_val, num_classes=10)
    y_test_encoded = to_categorical(y_test, num_classes=10)

    model = build_model()

    callbacks = [
        ModelCheckpoint(MODEL_PATH, monitor="val_accuracy", save_best_only=True, verbose=1),
        EarlyStopping(monitor="val_accuracy", patience=6, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
    ]

    history = model.fit(
        x_train,
        y_train_encoded,
        validation_data=(x_val, y_val_encoded),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    test_loss, test_accuracy = model.evaluate(x_test, y_test_encoded, verbose=0)
    probabilities = model.predict(x_test, verbose=0)
    predicted_labels = np.argmax(probabilities, axis=1)
    true_labels = y_test

    model.save(MODEL_PATH)
    history_data = save_history(history)
    save_training_curves(history)
    save_confusion_matrix_plot(true_labels, predicted_labels)
    save_sample_predictions(model, x_test, true_labels)

    summary = {
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "history": history_data,
        "artifacts": {
            "model": str(MODEL_PATH),
            "history": str(HISTORY_PATH),
            "training_curves": str(CURVE_PATH),
            "confusion_matrix": str(CONFUSION_MATRIX_PATH),
            "sample_predictions": str(SAMPLE_PREDICTIONS_PATH),
        },
    }

    print(json.dumps(summary, indent=2))
    return summary


def parse_args():
    parser = argparse.ArgumentParser(description="Train the handwritten digit CNN.")
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help="Path to the training CSV file.",
    )
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=DEFAULT_TEST_CSV,
        help="Path to the test CSV file.",
    )
    parser.add_argument(
        "--max-train-rows",
        type=int,
        default=20000,
        help="Maximum number of training rows to load for a faster local training run.",
    )
    parser.add_argument(
        "--max-test-rows",
        type=int,
        default=5000,
        help="Maximum number of test rows to load for a faster local training run.",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    train(
        arguments.train_csv,
        arguments.test_csv,
        arguments.epochs,
        arguments.batch_size,
        arguments.max_train_rows,
        arguments.max_test_rows,
    )