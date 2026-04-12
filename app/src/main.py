from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Модель данных для POST-запроса
class Item(BaseModel):
    name: str
    price: float


@app.get("/")
def read_root():
    return {"message": "Привет! Это GET запрос"}


@app.post("/items/")
def create_item(item: Item):
    return {"message": "Данные успешно получены", "received_item": item}
