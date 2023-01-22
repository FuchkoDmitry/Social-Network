import os
from dotenv import load_dotenv

from fastapi_mail import ConnectionConfig, FastMail

load_dotenv()

email_check_api_key = os.environ.get('EMAIL_CHECK_API_KEY')

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_FROM=os.environ.get('MAIL_FROM'),
    MAIL_SERVER=os.environ.get('MAIL_SERVER'),
    MAIL_PORT=os.environ.get('MAIL_PORT'),
    MAIL_FROM_NAME='testname',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)

fast_mail = FastMail(conf)
