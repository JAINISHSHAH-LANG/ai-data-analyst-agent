from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import pdfplumber
import os
import tempfile
from typing import List
from openai import OpenAI

# Initialize FastAPI app
app = FastAPI(title="AI Data Analyst Agent 🚀")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------- Utility functions ----------
def load_data(file: UploadFile):
    """Reads uploaded data file into DataFrame."""
    suffix = file.filename.split(".")[-1].lower()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}")
    tmp.write(file.file.read())
    tmp.close()

    if suffix in ["csv"]:
        return pd.read_csv(tmp.name)
    elif suffix in ["xls", "xlsx"]:
        return pd.read_excel(tmp.name)
    elif suffix in ["txt"]:
        return pd.read_csv(tmp.name, sep="\t")
    elif suffix in ["pdf"]:
        text = ""
        with pdfplumber.open(tmp.name) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def summarize_dataframe(df: pd.DataFrame) -> str:
    """Generate structured analysis summary of dataframe."""
    summary = {
        "shape": df.shape,
        "columns": list(df.columns),
        "null_values": df.isnull().sum().to_dict(),
        "summary_stats": df.describe(include="all").to_dict(),
        "correlations": df.corr(numeric_only=True).to_dict(),
    }
    return str(summary)


def ask_llm(question: str, context: str) -> str:
    """Ask OpenAI model with question + context."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a highly skilled Data Analyst."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ]
    )
    return response.choices[0].message.content


# ---------- API Endpoint ----------
@app.post("/analyze")
async def analyze_data(
    data_files: List[UploadFile] = File(...),
    questions_file: UploadFile = File(...)
):
    try:
        # Load data files
        dataframes = []
        text_data = []
        for f in data_files:
            loaded = load_data(f)
            if isinstance(loaded, pd.DataFrame):
                dataframes.append(loaded)
            else:
                text_data.append(loaded)

        # Merge dataframes if multiple
        if len(dataframes) > 0:
            df = pd.concat(dataframes, ignore_index=True)
            analysis_summary = summarize_dataframe(df)
        else:
            analysis_summary = "\n".join(text_data)

        # Load questions
        questions_content = load_data(questions_file)
        if isinstance(questions_content, pd.DataFrame):
            questions = " ".join(
                [str(q) for q in questions_content.iloc[:, 0].tolist()]
            )
        else:
            questions = str(questions_content)

        # Ask LLM
        answers = ask_llm(questions, analysis_summary)

        return JSONResponse({
            "status": "success",
            "questions": questions,
            "answers": answers
        })

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

