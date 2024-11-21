from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, select_autoescape, PackageLoader


# Configure Jinja2 environment
TEMPLATES = Environment(
    loader=PackageLoader("backend", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


router = APIRouter()

@router.get("/api/data", response_class=HTMLResponse)
async def get_data(request: Request):
    # You can add task data here for dynamic rendering
    task_data = {
        "todo": ["Task 1", "Task 2"],
        "in_progress": ["Task 3"],
        "done": ["Task 4"]
    }
    return TEMPLATES.get_template("index.html").render(request=request, tasks=task_data)
