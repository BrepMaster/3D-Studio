"""Flask 应用配置模块

负责创建和配置 Flask 应用实例。
"""

import os
from flask import Flask

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, template_folder=os.path.join(project_root, 'templates'))


def get_app() -> Flask:
    """获取 Flask 应用实例"""
    return app


def get_project_root() -> str:
    """获取项目根目录路径"""
    return project_root
