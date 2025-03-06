from fastapi import FastAPI
from app.routes import data_routes
from pydantic import BaseModel
import requests
import time
import random
from typing import List
from fake_useragent import UserAgent

ua = UserAgent()

class Ticket(BaseModel):
    tl_event_id: str
    tl_place_id: str
    tl_scene_id: str
    section_id: str
    section_name: str
    event_dt: str
    row: str
    place: str
    price: str

class EventResponse(BaseModel):
    status: str
    woplace: bool
    eventId: str
    tickets: List[Ticket]

app = FastAPI(title="Парсер API", root_path="/api/v1")

app.include_router(data_routes.router)


@app.get("/get-event/{event_id}", response_model=EventResponse)
def get_event_tickets(event_id: str):
    url = f"https://fomenki.ru/boxoffice/get/?event={event_id}"
    headers = {"User-Agent": ua.random}
    delay = random.uniform(3, 10)
    print(f'Запрос к URL: {url}. Ожидание {delay} секунд.')
    time.sleep(delay)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

    if not response.text.strip():
        return {"status": "error", "message": "Пустой ответ от API"}

    try:
        parsed_data = response.json()
    except requests.exceptions.JSONDecodeError:
        return {"status": "error", "message": "Ошибка при декодировании JSON"}

    tickets = [
        Ticket(
            tl_event_id=ticket["tl_event_id"],
            tl_place_id=ticket["tl_place_id"],
            tl_scene_id=ticket["tl_scene_id"],
            section_id=ticket["section_id"],
            section_name=ticket["section_name"],
            event_dt=ticket["event_dt"],
            row=ticket["row"],
            place=ticket["place"],
            price=ticket["price"]
        ) for ticket in parsed_data.get("tickets", [])
    ]

    return EventResponse(
        status=parsed_data.get("status", "unknown"),
        woplace=parsed_data.get("woplace", False),
        eventId=parsed_data.get("eventId", event_id),
        tickets=tickets
    )