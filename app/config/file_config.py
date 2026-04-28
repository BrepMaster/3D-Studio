"""文件配置模块

负责配置文件上传相关的参数。
"""

from typing import Set

ALLOWED_EXTENSIONS: Set[str] = {
    'step', 'stp', 'igs', 'iges', 'obj', 'gltf', 'glb', 'stl', '3ds', 'dae', 'fbx', '3mf'
}

MAX_FILE_SIZE: int = 100 * 1024 * 1024


def allowed_file(filename: str) -> bool:
    """检查文件是否为允许的类型"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
