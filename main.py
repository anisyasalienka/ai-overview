# from fastapi import FastAPI
# from pydantic import BaseModel
# from scraper import ai_overview_detector

# app = FastAPI()

# class KeywordsRequest(BaseModel) : 
#     keywords: str

# @app.get("/")
# async def read_root():
#     return {"message": "Hello, World!"}

# @app.post("/detect")
# async def detect(request: KeywordsRequest):
#     result = ai_overview_detector(request.keywords)
#     return {"result": result}

# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from scraper import ai_overview_detector
from scraper import main
from typing import List

app = FastAPI()
class KeywordsRequest(BaseModel):
    keywords: List[str]

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.post("/detect")
async def detect(request: KeywordsRequest):
    results = ai_overview_detector(request.keywords)
    simplified = [
        {
            "keyword": r["keyword"],
            "detected": r["detected"],
            "bot_detected": r.get("bot_detected", False)
        }
        for r in results
    ]
    return {"results": simplified}

