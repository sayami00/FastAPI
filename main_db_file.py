from typing import Union, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json

# Exception handling
app = FastAPI()

tasks_db = [] # In-memory database
DB_FILE = 'db.txt'


class TaskCreate(BaseModel):
    title: str
    description: str
    owner: str


class TaskResponse(TaskCreate):
    id: int
    is_completed: bool


def read_tasks_from_file() -> list[dict]:
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []
    
def write_tasks_to_file(tasks: list[dict]):
    with open(DB_FILE, 'w') as file:
        json.dump(tasks, file)


# Load tasks from file when application starts
@app.on_event("startup")
def startup_event():
    global tasks_db
    tasks_db = read_tasks_from_file()


@app.get('/')
def home():
    return {"message": "Welcome to task manager"}


@app.post('/tasks', response_model=TaskResponse)
def add_task(task: TaskCreate):
    task_dict = task.dict()
    task_dict['id'] = len(tasks_db) + 1
    task_dict['is_completed'] = False
    tasks_db.append(task_dict)
    write_tasks_to_file(tasks_db)
    return task_dict


@app.get('/tasks', response_model=List[TaskResponse])
def get_all_tasks():
    return tasks_db


@app.get('/tasks/owner/{owner}', response_model=List[TaskResponse])
def get_tasks_by_owner(owner: str):
    owner_tasks = [task for task in tasks_db if task['owner'] == owner]
    if not owner_tasks:
        raise HTTPException(status_code=404, detail=f"No tasks found for owner: {owner}")
    return owner_tasks


@app.get('/tasks/{task_id}', response_model=TaskResponse)
def get_task_by_id(task_id: int):
    for task in tasks_db:
        if task['id'] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put('/tasks/{task_id}/complete', response_model=TaskResponse)
def complete_task(task_id: int):
    for task in tasks_db:
        if task['id'] == task_id:
            task['is_completed'] = True  # Fixed: was using == instead of =
            write_tasks_to_file(tasks_db)  # Fixed: was writing single task instead of all tasks
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put('/tasks/{task_id}', response_model=TaskResponse)
def update_task(task_id: int, updated_task: TaskCreate):
    for task in tasks_db:
        if task['id'] == task_id:
            task['title'] = updated_task.title
            task['description'] = updated_task.description
            task['owner'] = updated_task.owner
            write_tasks_to_file(tasks_db)
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete('/tasks/{task_id}', response_model=dict)
def delete_task(task_id: int):
    global tasks_db
    
    for index, task in enumerate(tasks_db):
        if task['id'] == task_id:
            deleted_task = tasks_db.pop(index)
            write_tasks_to_file(tasks_db)
            return {"message": f"Task with id {task_id} has been deleted"}
    
    raise HTTPException(status_code=404, detail="Task not found")