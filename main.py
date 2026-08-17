from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from database import *
from supabase_client import supabase, sign_up_user, login, getUser_Token, log_out
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

secure = HTTPBearer()

class Task(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title:str
    done:bool

class SignupData(BaseModel):
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

app = FastAPI()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(secure)):
    token = credentials.credentials
    try:
        result = getUser_Token(token)
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})
    return result.user

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

@app.post("/auth/signup",status_code=201)
async def sign_up(sign_up_data: SignupData):
    if not sign_up_data.email or not sign_up_data.password:
        raise HTTPException(status_code=400, detail = {"error": f"Email and password required"})
    result = sign_up_user(sign_up_data.email, sign_up_data.password)
    return result

@app.post("/auth/login", status_code= 200)
async def sign_in_with_password(sign_in_data: LoginData):
    if not sign_in_data.email or not sign_in_data.password:
        raise HTTPException(status_code=400, detail = {"error": f"Email and password required"})
    try:
        result = login(sign_in_data.email, sign_in_data.password)
    except Exception:
        raise HTTPException(status_code=401, detail = {"error": f"Invalid login credentials"})
    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token
    }

@app.get("/public/info")
async def public_info():
    return {"message": "Welcome stranger! This info is public. "}

@app.get("/protected/profile")
async def protect(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

@app.post("/auth/logout", status_code=204)
async def logout(current_user = Depends(get_current_user)):
    log_out()
    return

@app.get("/protected/dashboard")
async def dashboard(current_user = Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {current_user.email}"}