import asyncio
import os
from dotenv import load_dotenv

from fastapi_mail import ConnectionConfig, FastMail, MessageType, MessageSchema

from .loggers import users_logger


load_dotenv()

email_check_api_key = os.environ.get('EMAIL_CHECK_API_KEY')

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get('MAIL_FROM'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_FROM=os.environ.get('MAIL_FROM'),
    MAIL_SERVER=os.environ.get('MAIL_SERVER'),
    MAIL_PORT=os.environ.get('MAIL_PORT'),
    MAIL_FROM_NAME='testname',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)

fast_mail = FastMail(conf)


def send_email(subject: str, recipients: list, body: str, subtype: MessageType = MessageType.plain):
    message = MessageSchema(
        subject=subject, recipients=recipients,
        body=body, subtype=subtype
    )
    try:
        result = fast_mail.send_message(message)
        asyncio.run(result)
        return {"status": "ok"}
    except Exception as err:
        users_logger.error(str(err))
        return {"status": str(err)}
