import pandas as pd
import io

def process_file(uploaded_file):
    filename = uploaded_file.filename
    content = uploaded_file.file.read()

    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(io.BytesIO(content))
    elif filename.endswith(".txt"):
        text = content.decode("utf-8")
        lines = text.splitlines()
        return [line.strip() for line in lines if line.strip()]
    else:
        raise ValueError("Unsupported file type. Use CSV, XLSX, or TXT.")

    return df.iloc[:, 0].dropna().astype(str).tolist()