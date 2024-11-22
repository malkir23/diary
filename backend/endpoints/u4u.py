from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, select_autoescape, PackageLoader


# Configure Jinja2 environment
TEMPLATES = Environment(
    loader=PackageLoader("backend", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


router = APIRouter()

@router.get("/table", response_class=HTMLResponse)
async def get_table(request: Request):
    # You can add task data here for dynamic rendering
    tasks_data = {
        "pre_flight": {
            "todo": ["Task 1", "Task 2"],
            "in_progress": ["Task 3"],
            "done": ["Task 4"]
        },
        "in_flight": {
            "todo": ["Task A"],
            "in_progress": ["Task B"],
            "done": ["Task C"]
        },
        "post_flight": {
            "todo": ["Task X"],
            "in_progress": [],
            "done": ["Task Y"]
        }
    }

    return TEMPLATES.get_template("index.html").render(request=request, tasks=tasks_data)
