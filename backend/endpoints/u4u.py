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
        "pre_flight": {"todo": ["Check tickets", "Pack luggage"], "done": ["Prepare documents"]},
        "in_flight": {"todo": ["Read book", "Eat snacks"], "done": ["Seatbelt on"]},
        "post_flight": {"todo": ["Collect luggage"], "done": ["Find transport"]},
    }
    return TEMPLATES.get_template("index.html").render(request=request, tasks=tasks_data)
