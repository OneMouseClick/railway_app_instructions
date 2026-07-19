import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from ai_engine import StationInstructionAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Генератор Инструкций Станций", version="1.0")

GIGACHAT_TOKEN = os.getenv("GIGACHAT_CREDENTIALS", "YOUR_GIGACHAT_TOKEN_HERE")

class GenerateRequest(BaseModel):
    passport_data: Dict[str, Any]

@app.post("/api/v1/generate")
def generate_instruction(request: GenerateRequest):
    meta_data = request.passport_data.get("meta", {})
    station_name = meta_data.get("station_name", "Неизвестная станция")
    
    ai = StationInstructionAI(gigachat_credentials=GIGACHAT_TOKEN)
    
    sections_to_generate = [
        "ОБЩАЯ ХАРАКТЕРИСТИКА ПУТИ НЕОБЩЕГО ПОЛЬЗОВАНИЯ",
        "ПОРЯДОК ПОДАЧИ И УБОРКИ ВАГОНОВ",
        "МАНЕВРОВАЯ РАБОТА",
        "ЗАКРЕПЛЕНИЕ ВАГОНОВ",
        "ТЕХНИКА БЕЗОПАСНОСТИ"
    ]
    
    document_sections = {}
    validation_errors = {}
    
    for section in sections_to_generate:
        print(f"Генерация раздела: {section}...")
        try:
            text = ai.generate_section(section, request.passport_data)
            document_sections[section] = text
        except Exception as e:
            print(f"Ошибка в разделе {section}: {str(e)}")
            document_sections[section] = "[ОШИБКА ГЕНЕРАЦИИ СЕРВИСОМ]"
            validation_errors[section] = str(e)
            
    response = {
        "status": "success" if not validation_errors else "completed_with_errors",
        "station": station_name,
        "document_sections": document_sections,
        "validation_errors": validation_errors
    }
    
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)