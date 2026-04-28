"""日志配置模块

负责配置应用的日志记录功能。
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_logger() -> logging.Logger:
    """获取日志记录器"""
    return logger


def set_log_level(level: int) -> None:
    """设置日志级别"""
    logger.setLevel(level)
