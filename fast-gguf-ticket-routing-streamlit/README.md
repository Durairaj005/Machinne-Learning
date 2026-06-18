# Fast GGUF Ticket Routing Streamlit Demo

This version is optimized for slower systems.

## Why it is faster

- The model loads only after clicking Route Ticket
- The model is cached after first load
- Context size is reduced to 512
- CPU threads are automatically selected
- Output is limited to a small number of tokens

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Important

If your model repo has more than one GGUF file, replace:

```python
MODEL_FILE = "*.gguf"
```

with the exact file name.