"""配置模块

此模块包含应用的所有配置信息，包括：
- Flask 应用配置
- 文件类型限制
- 文件大小限制
- 日志配置
"""

from .app_config import app, get_app, get_project_root
from .logging_config import get_logger, set_log_level
from .file_config import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    allowed_file
)

__all__ = [
    'app',
    'get_app',
    'get_logger',
    'set_log_level',
    'ALLOWED_EXTENSIONS',
    'MAX_FILE_SIZE',
    'allowed_file',
    'get_project_root'
]
