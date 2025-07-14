import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.core import config
from app.models.schemas import User

context = ssl.create_default_context()

templates_dir = Path(__file__).parent / "templates"
templates_env = Environment(loader=FileSystemLoader(str(templates_dir)))

def render_jinja_template(name: str, context: dict) -> str:
    template = templates_env.get_template(name)
    return template.render(**context)

def with_smtp_server(func):
    """
    Lets a function use the SMTP server to send an email.
    # Injects a variable called `server` which holds the `SMTP_SSL` object
    """
    def inner(*args, **kwargs):
        with smtplib.SMTP(config.SMTP_URL, config.SMTP_PORT) as server:
            # server.ehlo()
            # server.starttls(context=context)
            # server.ehlo()
            # server.login("username", "password")
            kwargs['server'] = server
            func(*args, **kwargs)
    return inner

@with_smtp_server
def send_verification_email(user: User, server: smtplib.SMTP | None = None):
    assert server is not None

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Your {config.PROJECT_NAME} Verification Code"
    message["From"] = config.APP_EMAIL_ADDRESS
    message["To"] = str(user.email)

    text = render_jinja_template("account_verification.txt", {"code": user.code})
    html = render_jinja_template("account_verification.html", {"code": user.code})

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    server.sendmail(config.APP_EMAIL_ADDRESS, str(user.email), message.as_string())
