"""核心功能模块

包含3D模型处理的核心功能：
- 文件读取
- 文件导出
- 剖切功能
- 模型分析
"""

from .readers import (
    read_step_file,
    read_iges_file,
    read_stl_file,
    read_file_by_extension,
    get_shape_topology_info,
    get_shape_physical_properties,
    get_shape_quality_report,
    get_model_info_quick
)
from .exporters import (
    shape_to_stl,
    shape_to_obj,
    shape_to_gltf,
    shape_to_step,
    shape_to_iges,
    get_output_format_info
)
from .section import (
    section_solid_by_planes,
    calculate_section_plane_position,
    get_bbox_center,
    create_section_plane,
    section_shape_by_plane
)

__all__ = [
    'read_step_file',
    'read_iges_file',
    'read_stl_file',
    'read_file_by_extension',
    'get_shape_topology_info',
    'get_shape_physical_properties',
    'get_shape_quality_report',
    'get_model_info_quick',
    'shape_to_stl',
    'shape_to_obj',
    'shape_to_gltf',
    'shape_to_step',
    'shape_to_iges',
    'get_output_format_info',
    'section_solid_by_planes',
    'calculate_section_plane_position',
    'get_bbox_center',
    'create_section_plane',
    'section_shape_by_plane'
]
