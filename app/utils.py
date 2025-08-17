import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import pdfplumber

def read_file(file):
    filename = file.filename.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(file.file)
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(file.file)
    elif filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    else:
        raise ValueError("Unsupported file type!")

def generate_line_chart(df, column, title="Line Chart"):
    plt.figure(figsize=(6,4))
    sns.lineplot(data=df, x=df.index, y=column, color='red')
    plt.title(title)
    plt.xlabel("Index")
    plt.ylabel(column)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_histogram(df, column, title="Histogram"):
    plt.figure(figsize=(6,4))
    sns.histplot(df[column], color='orange', kde=False, bins=10)
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel("Frequency")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def analyze_dataframe(df, questions=None):
    result = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        result[f"{col}_mean"] = df[col].mean()
        result[f"{col}_median"] = df[col].median()
        result[f"{col}_std"] = df[col].std()
    
    if len(numeric_cols) >= 2:
        result['correlation'] = df[numeric_cols].corr().to_dict()
    
    if numeric_cols:
        result['line_chart'] = generate_line_chart(df, numeric_cols[0])
        result['histogram'] = generate_histogram(df, numeric_cols[0])
    
    if questions:
        result['answered_questions'] = {q: "Answer generated using AI model" for q in questions}
    
    return result
