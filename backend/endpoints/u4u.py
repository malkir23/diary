from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


# Configure Jinja2 environment
TEMPLATES = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/api/data", response_class=HTMLResponse)
async def get_u4u_data(request: Request):
    # You can add task data here for dynamic rendering
    task_data = {
        "todo": ["Task 1", "Task 2"],
        "in_progress": ["Task 3"],
        "done": ["Task 4"]
    }
    return TEMPLATES.TemplateResponse("index.html", {"request": request, "tasks": task_data})
