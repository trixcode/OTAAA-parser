from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import os

router = APIRouter()

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "parser_full_event_data.json")
DATA_PATH_CRITICAL = os.path.join(os.path.dirname(__file__), "..", "storage", "critical_afishas_data.json")

@router.get("/data")
def get_parsed_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data, headers={"Content-Type": "application/json; charset=utf-8"})
    return JSONResponse(content={"error": "Data file not found"}, status_code=404)

@router.get("/critical")
def get_parsed_data_critical():
    if os.path.exists(DATA_PATH_CRITICAL):
        with open(DATA_PATH_CRITICAL, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data, headers={"Content-Type": "application/json; charset=utf-8"})
    return JSONResponse(content={"error": "Data file not found"}, status_code=404)
