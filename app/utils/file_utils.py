"""文件工具模块

提供文件相关的工具函数。
"""

import os
from typing import Optional


def format_file_size(bytes_size: int) -> str:
    """格式化文件大小为可读字符串"""
    if bytes_size < 1024:
        return f"{bytes_size:.2f} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"


def create_sample_shape(shape_type: str = 'box'):
    """创建示例几何形状"""
    try:
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCylinder
        
        if shape_type == 'sphere':
            return BRepPrimAPI_MakeSphere(1.0).Shape()
        elif shape_type == 'cylinder':
            return BRepPrimAPI_MakeCylinder(1.0, 2.0).Shape()
        else:
            return BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape()
    except ImportError:
        raise ImportError("需要安装 pythonocc-core 才能使用 create_sample_shape 函数")


def build_graph(solid) -> Optional[object]:
    """构建图神经网络（预留）"""
    try:
        from occwl.graph import face_adjacency
        return face_adjacency(solid)
    except ImportError:
        return None