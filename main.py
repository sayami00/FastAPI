
from typing import Union

from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import os
import json
#Exception  handling
app = FastAPI()

tasks_db = [] #sql Excel 



class TaskCreate(BaseModel):
    title:str
    description:str
    owner:str

class TaskResponse(TaskCreate):
    id:int
    is_completed:bool



@app.get('/home ')
def home():
    return {"message":"welcome to task manager"}
#{title : "eat something",description : "Please eat" ,owner : "ramesh"}

@app.post('/addtask',response_model=TaskResponse)
def add_task(task:TaskCreate):
    task_dict=task.dict()
    task_dict['id'] = len(tasks_db) + 1
    task_dict['is_completed'] = False
    tasks_db.append(task_dict)
    return task_dict


@app.get('/gettasks')
def get_all_tasks():
    return tasks_db


@app.get('/gettasks/{owner}')
def get_all_tasks(owner:str):
    for task in tasks_db:
        if  task['owner'] == owner:
            return task
    raise HTTPException(status_code=404,details="Task No Found")

@app.put('/completetask/{task_id}')
def complete_task(task_id:int) :
    for task in tasks_db:
        if task['id'] == task_id:
            task['is_completed'] == True
            return task
    raise HTTPException(status_code=404,detail="task not found")




