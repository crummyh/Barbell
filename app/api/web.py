from pathlib import Path
from typing import Annotated

import yaml
from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import TemplateNotFound
from sqlmodel import Session

from app.core import config
from app.core.dependencies import get_current_user
from app.core.helpers import get_team_number_from_id
from app.db.database import get_session
from app.models.models import UserOut, UserRole
from app.models.schemas import User

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(str(Path(BASE_DIR, config.TEMPLATES_PATH)))

# ========== { Public Pages } ========== #

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    user: User | None = Depends(get_current_user)
):
    if user is None:
        return templates.TemplateResponse(
            request=request, name="home.html", context={"user": None, "debug": config.DEBUG, "page": "index"}
        )

    user_out = UserOut(
        username=user.username,
        email=user.email,
        disabled=user.disabled,
        created_at=user.created_at,
        team_number=get_team_number_from_id(user.team, session),
        role=user.role
    )

    return templates.TemplateResponse(
        request=request, name="home.html", context={"user": user_out, "debug": config.DEBUG, "page": "index"}
    )

@router.get("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    user: User | None = Depends(get_current_user)
):
    if user is None:
        return templates.TemplateResponse(
            request=request, name="login.html", context={"user": None, "debug": config.DEBUG, "page": "login"}
        )

    return RedirectResponse("/dashboard")

@router.get("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    user: User | None = Depends(get_current_user)
):
    if user is None:
        return templates.TemplateResponse(
            request=request, name="register.html", context={"user": None, "debug": config.DEBUG, "page": "register"}
        )

    return RedirectResponse("/dashboard")

@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    user: User | None = Depends(get_current_user)
):
    if user is None:
        return templates.TemplateResponse(
            request=request, name="about.html", context={"user": None, "debug": config.DEBUG, "page": "about"}
        )

    user_out = UserOut(
        username=user.username,
        email=user.email,
        disabled=user.disabled,
        created_at=user.created_at,
        team_number=get_team_number_from_id(user.team, session),
        role=user.role
    )

    return templates.TemplateResponse(
        request=request, name="about.html", context={"user": user_out, "debug": config.DEBUG, "page": "about"}
    )

# ========== { Private Pages } ========== #

dashboard_structure = {
    UserRole.ADMIN: [
        {"title": "Home", "icon": "bi:house-fill", "slug": "home"},
        {"title": "Labels", "icon": "bi:list-ul", "slug": "labels"},
        {"title": "Rate-Limiting", "icon": "bi:speedometer", "slug": "ratelimit"},
    ],
    UserRole.MODERATOR: [
        {"title": "Home", "icon": "bi:house-fill", "slug": "home"},
        {"title": "Image Review", "icon": "bi:images", "slug": "image-review"},
    ],
    UserRole.DEFAULT: [
        {"title": "Home", "icon": "bi:house-fill", "slug": "home"},
        {"title": "Images", "icon": "bi:images", "slug": "images"},
        {"title": "Upload", "icon": "bi:cloud-upload-fill", "slug": "upload"},
        {"title": "Download", "icon": "bi:cloud-download-fill", "slug": "download"},
        {"title": "Settings", "icon": "bi:gear-fill", "slug": "settings"},
    ],
}

@router.get("/dashboard/{page}")
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    page: str = "home",
    user: User | None = Depends(get_current_user)
):
    if user is None:
        return RedirectResponse("/login")

    user_out = UserOut(
        username=user.username,
        email=user.email,
        disabled=user.disabled,
        created_at=user.created_at,
        team_number=get_team_number_from_id(user.team, session),
        role=user.role
    )

    page_title = None
    for section in dashboard_structure:
        if section == user.role:
            for _page in dashboard_structure[user.role]:
                if _page["slug"] == page:
                    page_title = _page["title"]

    if page_title is None:
        return not_found_page(request)

    template_name = f"dashboard/{user.role.name.lower()}/{page}.html"
    try:
        return templates.TemplateResponse(
            request=request, name=template_name, context={
                "user": user_out,
                "dashboard_structure": dashboard_structure[user.role],
                "current_page": page,
                "current_title": page_title,
                "debug": config.DEBUG,
                "page": "dashboard"
            }
        )
    except TemplateNotFound:
        print("Template not found: " + template_name)
        return not_found_page(request)

@router.get("/account", response_class=HTMLResponse)
async def account(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    user: User | None = Depends(get_current_user)
):
    if user is None:
        return RedirectResponse("/login")

    user_out = UserOut(
        username=user.username,
        email=user.email,
        disabled=user.disabled,
        created_at=user.created_at,
        team_number=get_team_number_from_id(user.team, session),
        role=user.role
    )

    return templates.TemplateResponse(
        request=request, name="account.html", context={"user": user_out, "debug": config.DEBUG, "page": "account"}
    )

# ========== { Docs } ========== #

docs_structure = [
    {
        "title": "Getting Started",
        "pages": [
            {"title": "Introduction", "slug": "introduction"},
            {"title": "Quickstart", "slug": "quickstart"},
            {"title": "Capture Setup", "slug": "capture"},
            {"title": "FAQ / Troubleshooting", "slug": "faq"}
        ],
    },
    {
        "title": "Using Data",
        "pages": [
            {"title": "Uploading", "slug": "upload"},
            {"title": "Downloading", "slug": "download"},
        ],
    },
    {
        "title": "API Guild",
        "pages": [
            {"title": "Authentication", "slug": "auth"},
            {"title": "Public API", "slug": "public"},
        ],
    },
    {
        "title": "Contributing",
        "pages": [
            {"title": "Moderating", "slug": "moderating"},
            {"title": "Developing", "slug": "developing"},
        ],
    },
    {
        "title": "Community",
        "pages": [
            {"title": "Roadmap", "slug": "roadmap"},
            {"title": "Discussions", "slug": "discussions"},
        ],
    },
]

@router.get("/docs/{page}", response_class=HTMLResponse)
@router.get("/docs", response_class=HTMLResponse)
async def docs(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    page: str = "introduction",
    user: User | None = Depends(get_current_user)
):
    user_out = None
    if user is not None:
        user_out = UserOut(
            username=user.username,
            email=user.email,
            disabled=user.disabled,
            created_at=user.created_at,
            team_number=get_team_number_from_id(user.team, session),
            role=user.role
        )

    if page == "api":
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Barbell - Swagger UI",
            swagger_favicon_url="/static/images/favicon.ico",
        )

    if page == "/api/redoc":
        return get_redoc_html(
            openapi_url="/openapi.json",
            title="Barbell - Redoc",
            redoc_favicon_url="/static/images/favicon.ico",
        )

    page_title = None
    for section in docs_structure:
        for _page in section["pages"]:
            if _page["slug"] == page:
                page_title = _page["title"]

    template_name = f"docs/{page}.html"
    try:
        return templates.TemplateResponse(
            request=request, name=template_name, context={
                "user": user_out,
                "docs_structure": docs_structure,
                "current_page": page,
                "current_title": page_title,
                "debug": config.DEBUG,
                "page": "docs"
            }
        )
    except TemplateNotFound as e:
        if config.DEBUG:
            raise e
        return not_found_page(request)


def load_snippets():
    snippets_dir = Path("/app/web/templates/docs/snippets")
    all_snippets = {}

    for file in snippets_dir.glob("*.yml"):
        data = yaml.safe_load(file.read_text())
        key = file.stem
        all_snippets[key] = data

    templates.env.globals["snippets"] = all_snippets

# ========== { Other } ========== #

def not_found_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="404.html", context={"user": None, "debug": config.DEBUG, "page": "404"}, status_code=404
    )
