from fastapi import FastAPI, HTTPException

app = FastAPI()

task_list= [{"id": 1, "title": "Study", "done": True}, {"id": 2, "title": "Exercise", "done": False}, {"id": 3, "title": "Shopping", "done": False}]

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