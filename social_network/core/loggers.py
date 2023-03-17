import logging
import logging.handlers
import logging.config
import os

from dotenv import load_dotenv

load_dotenv()

MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = os.environ.get("MAIL_PORT")
MAIL_FROM = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


class ErrorsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno > 31:
            return False
        return True


logging_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "sample_formatter": {
            "format": "[{asctime}] - [{levelname}] - [funcName {funcName} with args: {args}] - "
                      "[message: {message}] [pathname: {pathname}]",
                      # "[module:{module}] [process: {process}] [processname: {processName}] [thread {thread}] ["
                      # "threadName {threadName}] [line: {lineno}] ",
            "datefmt": "%d-%m-%y %H:%M:%S",
            "style": "{",
        },
        "error_formatter": {
            "format": "[{asctime}] - [levelname: {levelname}] - [funcName {funcName} at {pathname} in line №{lineno}] "
                      "- [error_message: {message}] - ",
            "datefmt": "%d-%m-%y %H:%M:%S",
            "style": "{"
        }
    },
    "handlers": {
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "sample_formatter",
            "filename": "logs/logs.log",
            "maxBytes": 10 * 1024,
            "backupCount": 2,
            "filters": ["errors_filter"]
        },
        "mail_handler": {
            "class": "logging.handlers.SMTPHandler",
            "formatter": "error_formatter",
            "level": "ERROR",
            "mailhost": MAIL_SERVER,
            "fromaddr": MAIL_FROM,
            "toaddrs": ["dmitrii.fuchko@yandex.ru"],
            "subject": "Attention from your app",
            "secure": (),
            "credentials": (MAIL_FROM, MAIL_PASSWORD),
        }
    },
    "loggers": {
        "users_logger": {
            "level": "INFO",
            "propagate": False,
            "handlers": ["file_handler", "mail_handler"],

        },
        "posts_logger": {
            "level": "INFO",
            "propagate": False,
            "handlers": ["file_handler", "mail_handler"]
        }
    },
    "filters": {
        "errors_filter": {
            "()": ErrorsFilter
        }
    }
}

logging.config.dictConfig(logging_config)

users_logger = logging.getLogger('users_logger')
posts_logger = logging.getLogger('posts_logger')

# #  for example
# def summ(a, b):
#     users_logger.info('func calls', {'a': 1, 'b': 2})
#     try:
#         result = a / b
#         users_logger.warning(f"result: {result}", {'a': 1, 'b': 2})
#         return result
#     except ZeroDivisionError as err:
#         users_logger.exception(str(err) + f'with args: {a, b}')
#
#
# summ(2, 0)
