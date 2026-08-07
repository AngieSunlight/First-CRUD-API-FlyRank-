from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from database import init_db

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
    if not task_data.title or task_data.title.strip() == "":
        raise HTTPException(status_code=400, detail={"error": "Title is required"})
    
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task_data.title,False,))
    conn.commit()
    next_id = cursor.lastrowid
    conn.close()
    new_task = {"id": next_id, "title": task_data.title.strip(), "done": False}
    return new_task

@app.put("/tasks/{id}")
async def replacement(id:int, task_data: TaskUpdate):
    """Lets you replace any task with validation"""
    if not task_data.title or not task_data.title.strip():
            raise HTTPException(status_code=400, detail={"error": "Title is required"})
    
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (task_data.title, task_data.done, id))
    conn.commit()
    #cursor.rowcount tells you how many rows the last query changed
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code = 404, detail = {"error": f"Task {id} not found"})
    conn.close()
    return {"id": id, "title": task_data.title.strip(), "done": task_data.done}

@app.delete("/tasks/{id}", status_code = 204)
async def delete_task(id: int):
    """Lets you remove a task"""
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail = {"error": f"Task {id} not found"})
    conn.commit()
    conn.close()
    return