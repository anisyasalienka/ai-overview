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
from scraper import scrape_keywords_from_spreadsheet
from scraper import save_results_to_excel
from scraper import save_results_in_chunks
from typing import List

# app = FastAPI()
class KeywordsRequest(BaseModel):
    keywords: List[str]

# Try to load keywords from the spreadsheet
try:
    keywords = scrape_keywords_from_spreadsheet()
    print(f"✅ Loaded {len(keywords)} keywords from Google Sheet.")
    results = ai_overview_detector(keywords)
    # save_results_in_chunks(results, chunk_size=100)



except Exception as e:
    print(f"❌ Failed to load keywords from spreadsheet: {e}")
    keywords = []  # fallback value, or you can raise an error if preferred



# @app.get("/")
# async def read_root():
#     return {"message": "Hello, World!"}

# @app.post("/detect")
# async def detect(request: KeywordsRequest):
#     results = ai_overview_detector(request.keywords)
#     simplified = [
#         {
#             "keyword": r["keyword"],
#             "detected": r["detected"],
#             "bot_detected": r.get("bot_detected", False)
#         }
#         for r in results
#     ]
#     return {"results": simplified}

