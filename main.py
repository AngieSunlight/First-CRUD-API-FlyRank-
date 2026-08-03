from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

task_list= [{"id": 1, "title": "Study", "done": True}, {"id": 2, "title": "Exercise", "done": False}, {"id": 3, "title": "Shopping", "done": False}]
    
class Task(BaseModel):
    title: str

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
    return task_list

@app.get("/tasks/{id}")
async def return_task(id: int):
    for task in task_list:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

@app.post("/tasks", status_code = 201)
async def add_task(task_data: Task):
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title is required"})
    next_id = max([t["id"] for t in task_list], default=0) + 1
    new_task = {"id": next_id, "title": task_data.title.strip(), "done": False}
    task_list.append(new_task)
    return new_task