"""响应处理模块

提供统一的响应创建和数据验证功能。
"""

from typing import Tuple, Dict
from flask import jsonify, Response


def create_error_response(error_message: str, status_code: int = 500) -> Tuple[Response, int]:
    """创建错误响应"""
    return jsonify({'error': error_message}), status_code


def validate_output_format(output_format: str) -> bool:
    """验证输出格式是否支持"""
    supported_formats = {'stl', 'obj', 'gltf', 'step', 'igs', 'bin'}
    return output_format.lower() in supported_formats


def parse_deflection_params(request_form: Dict) -> Tuple[float, float]:
    """解析网格化偏差参数"""
    try:
        linear_deflection = float(request_form.get('linear_deflection', 0.1))
    except (ValueError, TypeError):
        linear_deflection = 0.1

    try:
        angular_deflection = float(request_form.get('angular_deflection', 0.5))
    except (ValueError, TypeError):
        angular_deflection = 0.5

    linear_deflection = max(0.001, min(1.0, linear_deflection))
    angular_deflection = max(0.01, min(1.0, angular_deflection))

    return linear_deflection, angular_deflection