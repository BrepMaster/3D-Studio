"""剖切功能服务模块

负责处理模型剖切的业务逻辑。
"""

import os
from typing import Dict, List, Tuple

from app.config import get_logger, MAX_FILE_SIZE
from app.core import (
    read_file_by_extension,
    section_solid_by_planes,
    calculate_section_plane_position,
    get_bbox_center,
    create_section_plane,
    section_shape_by_plane,
    get_shape_topology_info,
    shape_to_stl,
    shape_to_obj,
    get_output_format_info
)
from app.utils import AsyncTaskManager
from app.temp_file_manager import temp_file

logger = get_logger()


class SectionService:
    """剖切功能服务"""

    def __init__(self):
        self.task_manager = AsyncTaskManager()

    def validate_file(self, file) -> Tuple[bool, str, int]:
        """验证文件"""
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return False, '文件大小超过限制（100MB）', 400

        ext = file.filename.rsplit('.', 1)[1].lower()
        return True, ext, file_size

    def process_section_slice(self, file, sections: List[Dict]) -> Dict:
        """处理剖切切片"""
        valid, ext_or_error, _ = self.validate_file(file)
        if not valid:
            raise ValueError(ext_or_error)

        ext = ext_or_error

        with temp_file(suffix=f'.{ext}') as input_path:
            file.save(input_path)

            def process():
                shape = read_file_by_extension(input_path, ext)
                bbox = get_shape_topology_info(shape)['bounding_box']

                planes_config = []
                for sec in sections:
                    axis = sec.get('axis', 'z')
                    offset = sec.get('offset', 0)
                    enabled = sec.get('enabled', True)

                    if not enabled:
                        continue

                    point, normal = calculate_section_plane_position(bbox, axis, offset)
                    planes_config.append({
                        'point': point,
                        'normal': normal,
                        'axis': axis,
                        'offset': offset
                    })

                if not planes_config:
                    raise Exception('没有启用的剖切平面')

                result = section_solid_by_planes(shape, planes_config)

                return {
                    'polylines': result.get('polylines', []),
                    'section_count': result.get('section_count', 0),
                    'bounding_box': bbox,
                    'center': get_bbox_center(bbox)
                }

            return self.task_manager.submit(process).result(timeout=45)

    def process_section_export(self, file, data: Dict) -> Tuple[str, str, str]:
        """处理剖切模型导出"""
        valid, ext_or_error, _ = self.validate_file(file)
        if not valid:
            raise ValueError(ext_or_error)

        ext = ext_or_error

        with temp_file(suffix=f'.{ext}') as input_path:
            file.save(input_path)

            def process():
                shape = read_file_by_extension(input_path, ext)

                output_format = data.get('output_format', 'stl').lower()
                linear_deflection = float(data.get('linear_deflection', 0.1))
                angular_deflection = float(data.get('angular_deflection', 0.5))

                output_suffix, mimetype = get_output_format_info(output_format)

                planes_config = []
                sections = data.get('sections', [])
                bbox = get_shape_topology_info(shape)['bounding_box']

                for sec in sections:
                    axis = sec.get('axis', 'z')
                    offset = sec.get('offset', 0)
                    enabled = sec.get('enabled', True)
                    keep_negative = sec.get('keep_negative', True)

                    if not enabled:
                        continue

                    point, normal = calculate_section_plane_position(bbox, axis, offset)
                    planes_config.append({
                        'point': point,
                        'normal': normal,
                        'keep_negative': keep_negative
                    })

                if planes_config:
                    for config in planes_config:
                        plane, _ = create_section_plane(config['point'], config['normal'])
                        section_result = section_shape_by_plane(shape, plane)
                        if section_result:
                            logger.info(f"剖切完成，获取 {section_result['edge_count']} 条切片边")

                with temp_file(suffix=output_suffix) as output_path:
                    if output_format == 'stl':
                        shape_to_stl(shape, output_path, linear_deflection, angular_deflection)
                    elif output_format == 'obj':
                        shape_to_obj(shape, output_path, linear_deflection, angular_deflection)
                    else:
                        shape_to_stl(shape, output_path, linear_deflection, angular_deflection)

                    return output_path, output_suffix, mimetype

            return self.task_manager.submit(process).result(timeout=60)