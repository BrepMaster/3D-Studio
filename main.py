"""3D Studio Web Application - 应用入口文件

项目简介:
    3D-Studio 是一个基于 Flask 和 PythonOCC 的 3D 模型转换与分析 Web 服务。
    提供多种 3D 文件格式转换、模型分析、剖切等功能。

主要功能:
    - 文件格式转换: STEP, IGES, STL, OBJ, GLTF, BIN
    - 模型分析: 拓扑信息、物理属性、质量评估
    - 剖切功能: 多平面剖切、切片数据提取
    - 历史管理: 版本控制、备份恢复
    - 批量处理: 批量文件转换

技术栈:
    - Web 框架: Flask
    - 3D 引擎: PythonOCC (OpenCASCADE)
    - 图神经网络: DGL (用于 BIN 格式)
    - 图像处理: PIL (缩略图生成)

目录结构:
    app/                    - 应用核心代码
    ├── __init__.py         - 应用包初始化，注册蓝图
    ├── routes.py           - 页面路由
    ├── config.py           - 配置管理
    ├── cache.py            - 缓存管理
    ├── readers.py          - 3D 文件读取
    ├── exporters.py        - 3D 文件导出
    ├── section.py          - 剖切平面功能
    ├── history.py          - 历史记录管理
    ├── helpers.py          - 辅助函数
    ├── validators.py       - 请求验证
    ├── temp_file_manager.py- 临时文件管理
    ├── utils.py            - 工具函数
    └── api/                - API 蓝图
        ├── __init__.py     - 蓝图包初始化
        ├── conversion.py   - 文件转换 API
        ├── history.py      - 历史记录 API
        ├── section.py      - 剖切功能 API
        └── model.py        - 模型分析 API
    templates/              - HTML 模板
    history/                - 历史记录存储

使用方式:
    直接运行此文件启动服务器:
        python main.py

    或通过 Python 导入启动:
        from app import run_server
        run_server(host='0.0.0.0', port=5000, debug=True)

作者: 3D Studio Team
版本: 1.2.0
"""

from app import run_server

if __name__ == '__main__':
    run_server()
