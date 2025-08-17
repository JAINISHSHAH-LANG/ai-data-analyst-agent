# app/__init__.py
"""
This file marks the app folder as a Python package.
No FastAPI routes should be defined here.
"""

import os

# Ensure OpenAI key is available
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError(
        "Missing OPENAI_API_KEY. Please set it in Render Dashboard under Environment Variables."
)





# # app/__init__.py
# from .main import app
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.responses import JSONResponse
# from typing import List, Optional
# import os
# import uuid
# from .processor import analyze_data  # your custom LLM/data analysis logic

# # Create necessary folders
# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# app = FastAPI(
#     title="AI Data Analyst Agent",
#     description="Upload your dataset and questions. Get precise analysis from AI.",
#     version="1.0.0",
# )


# @app.post("/api/")
# async def analyze(
#     questions: UploadFile = File(...),
#     files: Optional[List[UploadFile]] = None
# ):
#     """
#     Main endpoint for AI Data Analyst Agent.
#     Accepts:
#     - questions file (txt or pdf)
#     - optional dataset files (csv, excel, pdf)
#     Returns:
#     - JSON analysis results
#     """

#     try:
#         # Save questions file
#         questions_filename = f"{UPLOAD_FOLDER}/{uuid.uuid4()}_{questions.filename}"
#         with open(questions_filename, "wb") as f:
#             f.write(await questions.read())

#         # Save uploaded files
#         saved_files = []
#         if files:
#             for file in files:
#                 file_path = f"{UPLOAD_FOLDER}/{uuid.uuid4()}_{file.filename}"
#                 with open(file_path, "wb") as f:
#                     f.write(await file.read())
#                 saved_files.append(file_path)

#         # Perform data analysis
#         result = analyze_data(questions_filename, saved_files)

    #     return JSONResponse(content=result)

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

