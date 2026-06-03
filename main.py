from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, Mapped
from sqlalchemy.testing.schema import mapped_column
from starlette import status

DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker[Session](bind=engine)



class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True,default= lambda: str(uuid4()))

class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)

class CategoryORM(Base):
    __tablename__ = "categories"
    name: Mapped[str]

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield

app  = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)





class TaskSchema(BaseModel):
    id: str
    completed: bool
    title: str

class TaskCreateSchema(BaseModel):
    title:str

class TaskUpdateSchema(BaseModel):
    title:str|None = None
    completed:bool|None = None


class CategorySchema(BaseModel):
    id: str
    name: str

class CategoryCreateSchema(BaseModel):
    name:str

class CategoryUpdateSchema(BaseModel):
    name:str|None = None


categories : list[CategorySchema] = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def task_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(id=task_orm.id, completed=task_orm.completed, title=task_orm.title)

@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db))-> list[TaskSchema]:
    task_from_db = db.scalars(select(TaskORM)).all()
    return [task_to_model(task) for task in task_from_db]

@app.post("/tasks",status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema,db: Session = Depends(get_db))-> TaskSchema:
    new_task = TaskORM(title=payload.title,completed = False)
    db.add(new_task)
    db.commit()
    return task_to_model(new_task)



@app.patch("/tasks/{task_id}")
def update_task(task_id : str,payload: TaskUpdateSchema,db: Session = Depends(get_db)):
    task_for_update = db.get(TaskORM,task_id)
    if payload.title:
        task_for_update.title = payload.title
    if payload.completed:
        task_for_update.completed = payload.completed
    db.commit()
    return task_for_update


@app.delete("/tasks/{task_id}")
def delete_task(task_id : str,db: Session = Depends(get_db)):
    task_for_delete = db.get(TaskORM,task_id)
    db.delete(task_for_delete)
    db.commit()


def category_to_model(category_orm: CategoryORM) ->CategorySchema:
    return CategorySchema(id=category_orm.id,name = category_orm.name)

@app.get("/categories")
def read_categories(db: Session = Depends(get_db))-> list[CategorySchema]:
    category_from_db = db.scalars(select(CategoryORM)).all()

    return [category_to_model(category) for category in category_from_db]

@app.post("/categories")
def create_category(payload: CategoryCreateSchema,db: Session = Depends(get_db))-> CategorySchema:
    new_category = CategoryORM(name=payload.name)
    db.add(new_category)
    db.commit()
    return category_to_model(new_category)
@app.patch("/categories/{category_id}")
def update_category(category_id : str,payload: CategoryUpdateSchema,db: Session = Depends(get_db)):
    category_for_update = db.get(CategoryORM,category_id)
    if payload.name:
        category_for_update.name = payload.name
    db.commit()
    return category_for_update


@app.delete("/categories/{category_id}")
def delete_category(category_id : str,db: Session = Depends(get_db)):
    category_for_delete = db.get(CategoryORM,category_id)
    db.delete(category_for_delete)
    db.commit()

