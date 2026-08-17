from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import *
from supabase_client import supabase

class Task(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title:str
    done:bool

app = FastAPI()

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return{"name": "Task API",
           "version": "1.0",
           "endpoints": ["/tasks"]}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/tasks")
async def get_tasks():
    """Retrieves all tasks in the list"""
    return get_every_task()

@app.get("/tasks/{id}")
async def return_task(id: int):
    """Raises an error if the task doesn't exist"""
    row = specify_task(id)
    if row is None:
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
    return row

@app.post("/tasks", status_code = 201)
async def add_task(task_data: Task):
    """Creates a new task with validation"""
    if not task_data.title or task_data.title.strip() == "":
        raise HTTPException(status_code=400, detail={"error": "Title is required"})
    
    new_task = addition(task_data)
    return new_task

@app.put("/tasks/{id}")
async def replacement(id:int, task_data: TaskUpdate):
    """Lets you replace any task with validation"""
    if not task_data.title or not task_data.title.strip():
            raise HTTPException(status_code=400, detail={"error": "Title is required"})

    row = replace(id, task_data)
    #cursor.rowcount tells you how many rows the last query changed
    if row is None:
        raise HTTPException(status_code = 404, detail = {"error": f"Task {id} not found"})
    return row

@app.delete("/tasks/{id}", status_code = 204)
async def delete_task(id: int):
    """Lets you remove a task"""
    to_del = delete(id)
    if to_del is None:
        raise HTTPException(status_code=404, detail = {"error": f"Task {id} not found"})
    return