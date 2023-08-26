from typing import List
from backend.settings.config import settings
from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, select_autoescape, PackageLoader
from fastapi import Request, status, HTTPException
from datetime import datetime
from backend.quaries.users import Users
from backend.services.url import create_url


TEMPLATES = Environment(
    loader=PackageLoader("backend", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailService:
    def __init__(self, user_name: str, emails: list | str):
        self.name = user_name
        self.emails = self.create_emails_list(emails)

    def create_simple_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS = False,
            MAIL_SSL_TLS = False,
            USE_CREDENTIALS = True,
            VALIDATE_CERTS = True
        )

    async def create_html_message(
        self, subject: str, template_name: str, url: str, body_text: str
    ) -> str:
        # Generate the HTML template base on the template name
        template = TEMPLATES.get_template(f"{template_name}.html")

        html = template.render(
            url=url, first_name=self.name, subject=subject, body_text=body_text
        )

        # Define the message options
        message = MessageSchema(
            subject=subject, recipients=self.emails, body=html, subtype="html"
        )
        return message

    async def sendMail(self, template_name: str, message: str) -> None:
        # Send the email
        match template_name:
            case _:
                fast_mail = FastMail(self.create_simple_config())
        await fast_mail.send_message(message)

    def create_emails_list(self, emails: list[str] | str) -> List[EmailStr]:
        match emails:
            case str():
                new_emails = [EmailStr(email) for email in emails.split(",")]
            case list():
                new_emails = [EmailStr(email) for email in emails]
        return new_emails

    @classmethod
    async def error_email(cls, user_name: str, message: str) -> None:
        """Send a simple email
        """
        email = cls(user_name, settings.EMAILS_ERROR_SENDS_TO)
        template_name = "error"
        subject = "Error"
        message = await email.create_html_message(subject, template_name, None, message)
        await email.sendMail(template_name, message)

    @classmethod
    async def verify_email(
        cls, request: Request, token: str, user: dict, verification_type: str
    ) -> None:
        email = cls(user["username"], user["email"])
        template_name = "verification"
        try:
            match verification_type:
                case "forgot":
                    subject = "Password reset"
                    body_text = "Please click the link to reset your password."
                    url = f"{create_url(request)}/reset-password?token={token}"
                case "register":
                    subject = "Your verification code (Valid for 10min)"
                    body_text = """
                        Thanks for creating an account with us.
                        Please verify your email address by clicking the button below.
                    """
                    url = f"{create_url(request)}:{request.url.port}/api/auth/verify_email/{token}"

            message = await email.create_html_message(subject, template_name, url, body_text)
            await email.sendMail(template_name, message)

        except Exception as error:
            Users.find_one(
                {"_id": user["_id"]},
                {"$set": {"verification_code": None, "updated_at": datetime.utcnow()}},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There was an error sending email",
            )
