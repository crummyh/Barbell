from pathlib import Path
from typing import Annotated

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
from app.models.models import UserOut
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
            request=request, name="home.html", context={"user": None}
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
        request=request, name="home.html", context={"user": user_out}
    )

@router.get("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    user: User | None = Depends(get_current_user)
):
    if user is None:
        return templates.TemplateResponse(
            request=request, name="login.html", context={"user": None}
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
            request=request, name="register.html", context={"user": None}
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
            request=request, name="about.html", context={"user": None}
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
        request=request, name="about.html", context={"user": user_out}
    )

# ========== { Private Pages } ========== #

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
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
        request=request, name="dashboard-home.html", context={"user": user_out}
    )

@router.get("/dashboard/images", response_class=HTMLResponse)
async def dashboard_images(
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
        request=request, name="dashboard-images.html", context={"user": user_out}
    )

@router.get("/dashboard/upload", response_class=HTMLResponse)
async def dashboard_upload(
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
        request=request, name="dashboard-upload.html", context={"user": user_out}
    )

@router.get("/dashboard/download", response_class=HTMLResponse)
async def dashboard_download(
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
        request=request, name="dashboard-download.html", context={"user": user_out}
    )

@router.get("/dashboard/settings", response_class=HTMLResponse)
async def dashboard_settings(
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
        request=request, name="dashboard-settings.html", context={"user": user_out}
    )

@router.get("/dashboard/users", response_class=HTMLResponse)
async def dashboard_users(
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
        request=request, name="dashboard-users.html", context={"user": user_out}
    )

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
        request=request, name="account.html", context={"user": user_out}
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
            request=request, name=template_name, context={"user": user_out, "docs_structure": docs_structure, "current_page": page, "current_title": page_title}
        )
    except TemplateNotFound:
        return not_found_page(request)


# ========== { Other } ========== #

def not_found_page(request: Request):

    return templates.TemplateResponse(
        request=request, name="404.html", context={"user": None}, status_code=404
    )
