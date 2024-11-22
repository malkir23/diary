from unicodedata import category
from fastapi import Request, APIRouter, HTTPException
from typing import List
from fastapi.responses import HTMLResponse
from jinja2 import Environment, select_autoescape, PackageLoader
from backend.quaries.u4u import TASKS, CATEGORYS


# Configure Jinja2 environment
TEMPLATES = Environment(
    loader=PackageLoader("backend", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


router = APIRouter()

@router.get("/table", response_class=HTMLResponse)
async def get_table(request: Request):
    tasks = await TASKS.find()
    tasks_data = {}
    for task in tasks:
        tasks_data.setdefault(task["type"], []).append(task)

    return TEMPLATES.get_template("index.html").render(request=request, tasks=tasks_data)


@router.post("/tasks")
async def create_task(task: dict):
    return await TASKS.insert(task)

@router.get("/tasks")
async def list_tasks():
    return await TASKS.find()

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, updated_data: dict):
    updated = await TASKS.update({"id": task_id}, updated_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated successfully"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    deleted = await TASKS.delete({"id": task_id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@router.post("/categories")
async def create_category(category: dict):
    return await CATEGORYS.insert(category)

@router.get("/categories/list", response_class=HTMLResponse)
async def list_categories(request: Request):
    categories = await CATEGORYS.find()
    categories.sort(key=lambda x: x["id"])
    return TEMPLATES.get_template("categories.html").render(request=request, categories=categories)

@router.put("/categories/{category_id}")
async def update_category(category_id: int, updated_data: dict):
    updated = await CATEGORYS.update({"id": category_id}, updated_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category updated successfully"}

@router.delete("/categories/{category_id}")
async def delete_category(category_id: int):
    deleted = await CATEGORYS.delete({"id": category_id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
