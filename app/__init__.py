"""应用包初始化模块

此模块使 app 目录成为 Python 包，并负责导出主要的应用对象和服务器运行函数。
"""

import os

from app.routes import app, run_server

def register_blueprints():
    """注册所有蓝图到 Flask 应用"""
    from app.api import (
        conversion_bp,
        history_bp,
        section_bp,
        model_bp
    )

    app.register_blueprint(conversion_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(section_bp)
    app.register_blueprint(model_bp)

if os.environ.get('FLASK_ENV') != 'testing':
    register_blueprints()

__all__ = ['app', 'run_server']
__version__ = '1.2.0'