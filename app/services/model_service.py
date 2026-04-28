"""模型分析服务模块

负责处理模型分析的业务逻辑。
"""

import gc
from typing import Dict, Optional

from app.config import get_logger
from app.core import (
    read_file_by_extension,
    get_shape_topology_info,
    get_shape_physical_properties,
    get_shape_quality_report,
    get_model_info_quick
)
from app.temp_file_manager import temp_file

logger = get_logger()


class ModelService:
    """模型分析服务"""

    def get_model_info(self, file) -> Dict:
        """获取模型拓扑信息"""
        ext = file.filename.rsplit('.', 1)[1].lower()
        shape = None
        
        try:
            with temp_file(suffix=f'.{ext}') as input_path:
                file.save(input_path)
                shape = read_file_by_extension(input_path, ext)
                info = get_shape_topology_info(shape)
                info['filename'] = file.filename
                return info
        finally:
            del shape
            gc.collect()

    def get_model_physical_properties(self, file) -> Dict:
        """获取模型物理属性"""
        ext = file.filename.rsplit('.', 1)[1].lower()
        shape = None
        
        try:
            with temp_file(suffix=f'.{ext}') as input_path:
                file.save(input_path)
                shape = read_file_by_extension(input_path, ext)
                props = get_shape_physical_properties(shape)
                props['filename'] = file.filename
                return props
        finally:
            del shape
            gc.collect()

    def get_model_quality_report(self, file) -> Dict:
        """获取模型质量评估报告"""
        ext = file.filename.rsplit('.', 1)[1].lower()
        shape = None
        
        try:
            with temp_file(suffix=f'.{ext}') as input_path:
                file.save(input_path)
                shape = read_file_by_extension(input_path, ext)
                report = get_shape_quality_report(shape)
                report['filename'] = file.filename
                return report
        finally:
            del shape
            gc.collect()

    def get_model_info_quick(self, file) -> Dict:
        """快速获取模型基本信息"""
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        with temp_file(suffix=f'.{ext}') as input_path:
            file.save(input_path)
            info = get_model_info_quick(input_path)
            info['filename'] = file.filename
            return info