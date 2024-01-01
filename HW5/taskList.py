from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, MetaData, Table
import databases
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./test.db"
database = databases.Database(DATABASE_URL)
metadata = MetaData()

tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("description", String),
    Column("status", Boolean, default=False),
)

app = FastAPI()


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskResponse(TaskCreate):
    id: int
    status: bool


async def get_db():
    db = database
    try:
        yield db
    finally:
        pass


# Создание таблицы задач в базе данных
async def create_tasks_table():
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)


@app.on_event("startup")
async def startup_db_client():
    await database.connect()
    await create_tasks_table()


@app.on_event("shutdown")
async def shutdown_db_client():
    await database.disconnect()


# Заполнение базы данных начальными данными
@app.post("/tasks/fill_database/")
async def fill_database(db: databases.Database = Depends(get_db)):
    tasks_data = [
        {"title": "Купить горошек", "description": "Купить горошек до 31 декабря", "status": False},
        {"title": "Питон", "description": "Выучить Питон", "status": True},
        {"title": "FastAPI", "description": "Выучить FastAPI", "status": False},
    ]

    query = tasks.insert().values(tasks_data)
    await db.execute(query)
    return {"message": "БД заполнена данными"}


# Операция создания задачи
@app.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: databases.Database = Depends(get_db)):
    query = tasks.insert().values(**task.dict(), status=False)
    task_id = await db.execute(query)
    return {**task.dict(), "id": task_id, "status": False}


# Операция чтения всех задач
@app.get("/tasks/", response_model=list[TaskResponse])
async def read_tasks(db: databases.Database = Depends(get_db)):
    query = tasks.select()
    return await db.fetch_all(query)


# Операция чтения одной задачи по идентификатору
@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int, db: databases.Database = Depends(get_db)):
    query = tasks.select().where(tasks.c.id == task_id)
    task = await db.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


# Операция обновления задачи
@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskCreate, db: databases.Database = Depends(get_db)):
    query = tasks.update().where(tasks.c.id == task_id).values(**task.dict())
    await db.execute(query)
    return {**task.dict(), "id": task_id, "status": False}


# Операция удаления задачи
@app.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int, db: databases.Database = Depends(get_db)):
    query = tasks.delete().where(tasks.c.id == task_id)
    task = await db.execute(query)
    if task.rowcount == 0:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"id": task_id, **task.dict(), "status": False}
