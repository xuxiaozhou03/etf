"""日志配置模块"""

import logging
import sys
from .settings import settings


def setup_logging() -> None:
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)
