from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

task_list= [{"id": 1, "title": "Study", "done": True}, {"id": 2, "title": "Exercise", "done": False}, {"id": 3, "title": "Shopping", "done": False}]
    
class Task(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title:str
    done:bool

app = FastAPI()

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
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/tasks/{id}")
async def return_task(id: int):
    """Raises an error if the task doesn't exist"""
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
    return dict(row)

@app.post("/tasks", status_code = 201)
async def add_task(task_data: Task):
    """Creates a new task with validation"""
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title is required"})
    next_id = max([t["id"] for t in task_list], default=0) + 1
    new_task = {"id": next_id, "title": task_data.title.strip(), "done": False}
    task_list.append(new_task)
    return new_task

@app.put("/tasks/{id}")
async def replacement(id:int, task_data: TaskUpdate):
    """Lets you replace any task with validation"""
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title is required"})
    for task in task_list:
        if task["id"] == id:
            task["title"] = task_data.title.strip()
            task["done"] = task_data.done
            return task
    raise HTTPException(status_code = 404, detail = {"error": f"Task {id} not found"})

@app.delete("/tasks/{id}", status_code = 204)
async def delete_task(id: int):
    """Lets you remove a task"""
    for task in task_list:
        if task["id"] == id:
            task_list.remove(task)
            return
    raise HTTPException(status_code=404, detail = {"error": f"Task {id} not found"})