from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional
import pandas as pd
from app import utils

app = FastAPI(title="AI Data Analyst Agent API 🚀")

@app.post("/api/")
async def analyze(
    questions_file: UploadFile,
    data_files: Optional[List[UploadFile]] = None
):
    try:
        questions_text = utils.read_file(questions_file)
        questions = []
        if isinstance(questions_text, str):
            questions = [line.strip() for line in questions_text.split("\n") if line.strip()]
        elif isinstance(questions_text, pd.DataFrame):
            questions = questions_text.iloc[:,0].astype(str).tolist()
        
        analyses = {}
        if data_files:
            for file in data_files:
                content = utils.read_file(file)
                if isinstance(content, pd.DataFrame):
                    analyses[file.filename] = utils.analyze_dataframe(content, questions)
                else:
                    analyses[file.filename] = {"content": content}
        
        return JSONResponse(content={
            "questions": questions,
            "analysis": analyses
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
