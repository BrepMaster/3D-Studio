"""测试配置文件

此模块配置测试运行环境和测试用例。

运行测试:
    python -m pytest tests/ -v
    python -m pytest tests/ -v --cov=app
    python -m pytest tests/ -v -k "test_name"
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['FLASK_ENV'] = 'testing'


@pytest.fixture
def app():
    """创建测试用的 Flask 应用"""
    from app.config import get_app
    app = get_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def sample_step_content():
    """返回有效的 STEP 文件内容（头部）"""
    return """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Open CASCADE Model'),'2;1');
FILE_NAME('test.step','2024-01-01T00:00:00',('author'),(''),'Open CASCADE','Open CASCADE','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
ENDSEC;
DATA;
#1 = APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#2);
"""


@pytest.fixture
def sample_stl_content():
    """返回有效的 STL 文件内容"""
    return """solid test
  facet normal 0 0 1
    outer loop
      vertex 0 0 0
      vertex 1 0 0
      vertex 0 1 0
    endloop
  endfacet
endsolid test
"""


@pytest.fixture
def temp_history_dir(tmp_path):
    """创建临时历史目录"""
    history_dir = tmp_path / "history"
    history_dir.mkdir()
    return str(history_dir)
