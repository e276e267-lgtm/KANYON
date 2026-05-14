from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from parser import analyze

app = FastAPI(title="Y5 數字判別 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    sequence: str

@app.post("/analyze")
def run_analysis(data: InputData):
    res = analyze(data.sequence)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.get("/")
def root():
    return {"message": "Y5 數字判別服務運行中", "endpoint": "POST /analyze"}