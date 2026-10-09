import logging
import os
import sys
import traceback
from datetime import datetime

from loguru import logger as base_logger
from pydantic import BaseModel

DEV_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{extra[package]}</cyan> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


class ExceptionData(BaseModel):
    type: str
    message: str
    traceback: str


class LogData(BaseModel):
    timestamp: datetime
    level: str
    message: str
    logger: str
    function: str
    line: int
    package: str | None = None
    exception: ExceptionData | None = None


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = base_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        base_logger.bind(package=record.name).opt(
            exception=record.exc_info,
            depth=6,
        ).log(level, record.getMessage())


def json_sink(message) -> None:
    record = message.record
    exception = record["exception"]

    log_data = LogData(
        timestamp=record["time"],
        level=record["level"].name,
        message=record["message"],
        logger=record["name"],
        function=record["function"],
        line=record["line"],
        package=record["extra"].get("package"),
        exception=(
            ExceptionData(
                type=exception.type.__name__,
                message=str(exception.value),
                traceback="".join(
                    traceback.format_exception(
                        exception.type,
                        exception.value,
                        exception.traceback,
                    )
                ),
            )
            if exception
            else None
        ),
    )

    print(
        log_data.model_dump_json(exclude_none=True),
        file=sys.stderr,
        flush=True,
    )


class LogManager:
    def __init__(self):
        self.level = os.getenv("LOG_LEVEL", "INFO")
        self.is_prod = os.getenv("LOG_PROD", "false") == "true"
        self._configure()

    def _configure(self) -> None:
        base_logger.remove()

        if self.is_prod:
            base_logger.add(
                json_sink,
                level=self.level,
            )
        else:
            base_logger.add(
                sys.stderr,
                level=self.level,
                format=DEV_FORMAT,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )

        logging.basicConfig(
            handlers=[InterceptHandler()],
            level=self.level,
            force=True,
        )

        for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            uvicorn_logger = logging.getLogger(logger_name)
            uvicorn_logger.handlers = [InterceptHandler()]
            uvicorn_logger.setLevel(self.level)
            uvicorn_logger.propagate = False

    @staticmethod
    def get_logger(package: str):
        return base_logger.bind(package=package)


log_manager = LogManager()


def get_logger(package: str):
    return log_manager.get_logger(package)
