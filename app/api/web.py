from pathlib import Path

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core import config

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(str(Path(BASE_DIR, config.TEMPLATES_PATH)))

# ========== { Public Pages } ========== #

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={}
    )

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html", context={}
    )

@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse(
        request=request, name="register.html", context={}
    )

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        request=request, name="about.html", context={}
    )

# ========== { Private Pages } ========== #

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={}
    )

@router.get("/acount", response_class=HTMLResponse)
async def acount(request: Request):
    return templates.TemplateResponse(
        request=request, name="acount.html", context={}
    )

# ========== { Internal Pages } ========== #

@router.get("/moderation", response_class=HTMLResponse)
async def moderation(request: Request):
    return templates.TemplateResponse(
        request=request, name="moderation.html", context={}
    )

@router.get("/labeling", response_class=HTMLResponse)
async def labeling(request: Request):
    return templates.TemplateResponse(
        request=request, name="labeling.html", context={}
    )

# ========== { Docs } ========== #


@router.get("/docs", response_class=HTMLResponse)
async def docs(request: Request):
    return templates.TemplateResponse(
        request=request, name="docs.html", context={}
    )


@router.get("/docs/tools", response_class=HTMLResponse)
async def tool_docs(request: Request):
    return templates.TemplateResponse(
        request=request, name="tool-docs.html", context={}
    )
