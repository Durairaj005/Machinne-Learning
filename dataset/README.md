Dataset for Digit Recognition AI

Files
- mnist_train.csv — training set (CSV of labeled digit images/features).
- mnist_test.csv — test set (CSV of labeled digit images/features).
- archives/testSet.tar.gz — archived additional test data (extract if needed).
- .gitkeep — placeholder to keep the dataset directory in version control.

Usage
- Place or keep dataset files in this folder; training and inference scripts
  in `backend/` expect datasets to be available here.
- If you need to inspect the archive: extract `archives/testSet.tar.gz`.

Notes
- Verify CSV formats before training (headers, separators, label column).
- If these files are large, consider storing them outside the repo and
  updating paths in `backend/train_model.py` accordingly.
