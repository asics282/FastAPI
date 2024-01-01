from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="HW4/templates")  # создание объекта шаблонов


# Модель для данных о музыке
class MusicItem(BaseModel):
    song: str
    artist: str


# Список музыки
music_db = [
    MusicItem(song="Три белых коня", artist="Лариса Долина"),
    MusicItem(song="Last Christmas", artist="Wham!"),
    MusicItem(song="Три Зимы", artist="Таисия Повалий"),
    MusicItem(song="Звенит январская вьюга", artist="нина Бродская"),
    MusicItem(song="Новогодняя", artist="Верка Сердючка")
]


# Отображение HTML-страницы со списком музыки
@app.get("/", response_class=HTMLResponse)
async def read_music_list(request: Request):
    return templates.TemplateResponse("music_list.html", {"request": request, "music_list": music_db})


# Добавление музыки в список
@app.post("/add_music/")
async def add_music(item: MusicItem):
    music_db.append(item)
    return {"message": "Музыка успешно добавлена"}


# Обновление списка музыки
@app.put("/update_music/")
async def update_music(new_music_list: List[MusicItem]):
    music_db.clear()
    music_db.extend(new_music_list)
    return {"message": "Список музыки успешно обновлен"}


# Удаление музыки из списка
@app.delete("/delete_music/{index}")
async def delete_music(index: int):
    try:
        deleted_item = music_db.pop(index)
        return {"message": f"Музыка {deleted_item.song} - {deleted_item.artist} удалена"}
    except IndexError:
        raise HTTPException(status_code=404, detail="Элемент не найден")
