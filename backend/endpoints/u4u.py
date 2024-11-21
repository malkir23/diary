from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, select_autoescape, PackageLoader


# Configure Jinja2 environment
TEMPLATES = Environment(
    loader=PackageLoader("backend", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


router = APIRouter()

@router.get("/api/data")
async def get_data():
    template = TEMPLATES.get_template("index.html")
    rendered_html = template.render(user="Alice")  # Pass dynamic data to the template
    return HTMLResponse(content=rendered_html)
