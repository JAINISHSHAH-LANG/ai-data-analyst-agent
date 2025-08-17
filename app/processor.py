# app/processor.py
import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import List, Dict
from openai import OpenAI  # or any LLM you choose
import os

# Initialize LLM client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def read_questions(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError("Questions file must be .txt or .pdf")

def read_data_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    elif ext == ".pdf":
        text = extract_text_from_pdf(file_path)
        # Simple CSV-like parsing from PDF text
        from io import StringIO
        return pd.read_csv(StringIO(text))
    else:
        raise ValueError(f"Unsupported data file type: {ext}")

def generate_base64_plot(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_bytes = buf.getvalue()
    buf.close()
    return base64.b64encode(img_bytes).decode("utf-8")

def analyze_data(questions_file: str, data_files: List[str]) -> Dict:
    # Extract questions
    questions_text = read_questions(questions_file)

    # Read all data files into one dataframe (concatenate)
    dfs = []
    for f in data_files:
        dfs.append(read_data_file(f))
    if dfs:
        data = pd.concat(dfs, ignore_index=True)
    else:
        data = pd.DataFrame()

    # Prepare basic analysis
    analysis = {}
    if not data.empty:
        # Example statistics
        analysis["summary_stats"] = data.describe(include="all").to_dict()

        # Generate sample visualization for numeric columns
        numeric_cols = data.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            fig, ax = plt.subplots()
            data[numeric_cols[0]].plot(kind="line", ax=ax, color="red", title=numeric_cols[0])
            ax.set_xlabel("Index")
            ax.set_ylabel(numeric_cols[0])
            analysis["sample_line_chart"] = generate_base64_plot(fig)
            plt.close(fig)

    # Call LLM to answer the uploaded questions
    llm_prompt = f"Data:\n{data.head(20).to_csv(index=False)}\n\nQuestions:\n{questions_text}\n\nAnswer the questions based on this data."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": llm_prompt}],
        temperature=0
    )
    analysis["answers"] = response.choices[0].message.content

    return analysis
