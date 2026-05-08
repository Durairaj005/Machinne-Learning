# AI Handwritten Digit Recognition System

Modern handwritten digit recognition web app built with a TensorFlow/Keras CNN backend and a React + Tailwind + Framer Motion frontend.

## Features

- CNN trained on the Kaggle MNIST CSV train/test files
- FastAPI REST endpoint for prediction
- Animated React dashboard with drag-and-drop upload
- Drawing canvas with live prediction
- Accuracy and loss charts, confusion matrix, and sample prediction gallery
- Prediction history, download as PNG/PDF, and sound feedback
- Built as a local website demo for presentation in VS Code

## Project Structure

```text
digit-recognition-ai/
├── backend/
│   ├── app.py
│   ├── predict.py
│   ├── train_model.py
│   ├── model/
│   │   └── digit_model.h5
│   └── requirements.txt
├── dataset/
│   ├── mnist_train.csv
│   ├── mnist_test.csv
│   └── archives/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## Dataset Setup

The training script expects the Kaggle CSV files in the `dataset/` folder:

```text
dataset/mnist_train.csv
dataset/mnist_test.csv
```

The CSVs should contain a `label` column and 784 pixel columns.

## Backend Setup

1. Open a terminal in VS Code and go to `backend`.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Train the model from the CSV files:

```bash
python train_model.py --train-csv ..\dataset\mnist_train.csv --test-csv ..\dataset\mnist_test.csv --epochs 20
```

5. Start the API:

```bash
uvicorn app:app --reload --port 8000
```

API endpoints:

- `GET /health`
- `GET /metrics`
- `POST /predict`

## Frontend Setup

1. Open a second terminal in VS Code and go to `frontend`.
2. Install dependencies:

```bash
npm install
```

3. Create a local `.env` file if needed:

```bash
VITE_API_URL=http://localhost:8000
```

4. Start the React app:

```bash
npm run dev
```

## How To Run in VS Code

1. Open the `digit-recognition-ai` folder in VS Code.
2. Run the backend training command once to create `backend/model/digit_model.h5`.
3. Start `uvicorn` in one terminal.
4. Start `npm run dev` in another terminal.
5. Open the frontend URL shown by Vite and upload a digit image or draw one on the canvas.

## Notes

- The current code expects the Kaggle MNIST CSV files in `dataset/`.
- The frontend already includes download, history, and live canvas prediction features.
