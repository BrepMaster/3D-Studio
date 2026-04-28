"""验证器模块

提供各种数据验证函数。
"""

import re
from typing import Tuple, Dict, Any, Optional


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """验证文件扩展名是否支持"""
    if not filename:
        return False, '文件名不能为空'
    
    if '.' not in filename:
        return False, '缺少扩展名'
    
    ext = filename.rsplit('.', 1)[-1].lower()
    supported_extensions = {'step', 'stp', 'iges', 'igs', 'stl', 'obj', '3mf'}
    
    if ext in supported_extensions:
        return True, ext
    
    return False, f'不支持的文件格式: {ext}'


def validate_output_format(output_format: str) -> Tuple[bool, Optional[str]]:
    """验证输出格式是否支持"""
    if not output_format:
        return False, '输出格式不能为空'
    
    supported_formats = {'stl', 'obj', 'step', 'iges', 'igs', 'gltf', 'bin'}
    
    if output_format.lower() in supported_formats:
        return True, None
    
    return False, f'不支持的输出格式: {output_format}'


def validate_deflection_params(linear: Any, angular: Any) -> Tuple[bool, float, float, Optional[str]]:
    """验证网格化偏差参数"""
    try:
        linear_deflection = float(linear) if linear is not None else 0.1
    except (ValueError, TypeError):
        return False, 0.1, 0.5, '线性偏差参数无效'
    
    try:
        angular_deflection = float(angular) if angular is not None else 0.5
    except (ValueError, TypeError):
        return False, 0.1, 0.5, '角度偏差参数无效'
    
    if linear_deflection < 0.001 or linear_deflection > 1.0:
        return False, linear_deflection, angular_deflection, '线性偏差值应在 0.001 到 1.0 之间'
    
    if angular_deflection < 0.01 or angular_deflection > 1.0:
        return False, linear_deflection, angular_deflection, '角度偏差值应在 0.01 到 1.0 之间'
    
    return True, linear_deflection, angular_deflection, None


def validate_section_config(config: Dict) -> Tuple[bool, Optional[str]]:
    """验证剖切配置"""
    if not isinstance(config, dict):
        return False, '剖切配置必须是字典类型'
    
    if 'axis' not in config:
        return False, '剖切配置缺少轴参数'
    
    axis = config.get('axis', '').lower()
    if axis not in {'x', 'y', 'z'}:
        return False, '无效的轴参数，必须是 x、y 或 z'
    
    offset = config.get('offset', 0)
    if not isinstance(offset, (int, float)):
        return False, '偏移值必须是数字'
    
    if offset < -100 or offset > 100:
        return False, '偏移值应在 -100 到 100 之间'
    
    return True, None


def validate_bbox(bbox: Dict) -> Tuple[bool, Optional[str]]:
    """验证 bounding box"""
    if not isinstance(bbox, dict):
        return False, 'bounding box 必须是字典类型'
    
    required_keys = {'min', 'max', 'size'}
    if not required_keys.issubset(bbox.keys()):
        return False, '缺少必需的键: min、max 或 size'
    
    for key in ['min', 'max', 'size']:
        value = bbox[key]
        if not isinstance(value, list) or len(value) != 3:
            return False, f'{key} 必须是包含3个元素的列表'
        
        for coord in value:
            if not isinstance(coord, (int, float)):
                return False, f'{key} 的元素必须是数字'
    
    return True, None


def validate_history_id(history_id: str) -> Tuple[bool, Optional[str]]:
    """验证历史记录ID是否为有效的UUID"""
    if not history_id:
        return False, '历史记录ID不能为空'
    
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    
    if not re.match(uuid_pattern, history_id.lower()):
        return False, '无效的历史记录ID格式'
    
    return True, None


def validate_search_params(params: Dict) -> Tuple[bool, Optional[str]]:
    """验证搜索参数"""
    if not isinstance(params, dict):
        return False, '搜索参数必须是字典类型'
    
    if 'min_size' in params:
        try:
            min_size = int(params['min_size'])
            if min_size < 0:
                return False, '最小文件大小不能为负数'
        except (ValueError, TypeError):
            return False, '最小文件大小必须是整数'
    
    if 'max_size' in params:
        try:
            max_size = int(params['max_size'])
            if max_size < 0:
                return False, '最大文件大小不能为负数'
        except (ValueError, TypeError):
            return False, '最大文件大小必须是整数'
    
    if 'min_size' in params and 'max_size' in params:
        try:
            min_size = int(params['min_size'])
            max_size = int(params['max_size'])
            if min_size > max_size:
                return False, '最小文件大小不能大于最大文件大小'
        except (ValueError, TypeError):
            pass
    
    return True, None