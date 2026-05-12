from uuid import uuid4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app  = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],

)

tasks: list[TaskSchema] = []

class TaskSchema(BaseModel):
    id: str
    completed: bool
    title: str

class TaskCreateSchema(BaseModel):
    title:str

@app.get("/tasks")
def read_tasks()-> list[TaskSchema]:
    return tasks

@app.post("/tasks")
def create_task(payload: TaskCreateSchema)-> TaskSchema:
    new_task = TaskSchema(id=str(uuid4()), completed=False, title=payload.title)
    tasks.append(new_task)
    return new_task

book:str = ""
class BookSchema(BaseModel):
    title: str

@app.get("/book")
def read_books()-> str:
    return f"Любимая книга: {book}"
@app.post("/book")
def create_book(payload: BookSchema)-> str:
    global book
    book = payload.title
    return book