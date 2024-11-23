from typing import Union

from fastapi import FastAPI, Request, Form
from service import data_compaire
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import re
app = FastAPI()


def validate_and_process_input(input_text: str, max_query_length: int = 100) -> list:
    if not input_text.strip():
        raise ValueError("Ввод не должен быть пустым")

    # Разделение по запятым
    queries = input_text.split(',')

    # Очистка пробелов и удаление пустых запросов
    queries = [query.strip() for query in queries if query.strip()]

    # Ограничение длины каждого запроса
    queries = [query for query in queries if len(query) <= max_query_length]

    # Удаление лишних символов
    queries = [re.sub(r'[^a-zA-Zа-яА-Я0-9\s\?,]', '', query) for query in queries]

    if not queries:
        raise ValueError("Все запросы некорректны или превышают допустимую длину")

    return queries


templates = Jinja2Templates(directory="templates")


@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...)):
    try:
        data_set = validate_and_process_input(user_input)
    except Exception as e:
        return str(e)
    data = await data_compaire(data_set)
    context = {"request": request, "data": data}
    return templates.TemplateResponse("index.html", context)


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})
