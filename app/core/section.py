"""模型剖切功能模块

负责处理3D模型的剖切操作，包括多平面剖切和切片数据提取。
"""

from typing import Dict, List, Tuple, Any
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE

from app.config import get_logger

logger = get_logger()


def get_bbox_center(bbox: Dict[str, Any]) -> List[float]:
    """获取边界框中心"""
    min_point = bbox['min']
    max_point = bbox['max']
    return [
        (min_point[0] + max_point[0]) / 2,
        (min_point[1] + max_point[1]) / 2,
        (min_point[2] + max_point[2]) / 2
    ]


def calculate_section_plane_position(bbox: Dict[str, Any], axis: str, offset: float) -> Tuple[List[float], List[float]]:
    """计算剖切平面位置"""
    center = get_bbox_center(bbox)
    size = bbox['size']

    if axis == 'x':
        point = [center[0] + offset * size[0] / 2, center[1], center[2]]
        normal = [1, 0, 0]
    elif axis == 'y':
        point = [center[0], center[1] + offset * size[1] / 2, center[2]]
        normal = [0, 1, 0]
    else:
        point = [center[0], center[1], center[2] + offset * size[2] / 2]
        normal = [0, 0, 1]

    return point, normal


def create_section_plane(point: List[float], normal: List[float]) -> Tuple[gp_Pln, gp_Dir]:
    """创建剖切平面"""
    pnt = gp_Pnt(point[0], point[1], point[2])
    dir_vec = gp_Dir(normal[0], normal[1], normal[2])
    plane = gp_Pln(pnt, dir_vec)
    return plane, dir_vec


def section_shape_by_plane(shape, plane: gp_Pln) -> Dict[str, Any]:
    """使用平面对形状进行剖切"""
    try:
        section = BRepAlgoAPI_Section()
        section.AddShape(shape)
        section.SetPlane(plane)
        section.Build()

        if not section.IsDone():
            return {'error': '剖切操作失败'}

        result_shape = section.Shape()

        edge_count = 0
        explorer = TopExp_Explorer(result_shape, TopAbs_EDGE)
        while explorer.More():
            edge_count += 1
            explorer.Next()

        return {
            'success': True,
            'shape': result_shape,
            'edge_count': edge_count
        }
    except Exception as e:
        logger.error(f'剖切操作失败: {e}')
        return {'error': str(e)}


def section_solid_by_planes(shape, planes_config: List[Dict[str, Any]]) -> Dict[str, Any]:
    """使用多个平面对实体进行剖切"""
    results = []

    for plane_config in planes_config:
        point = plane_config['point']
        normal = plane_config['normal']
        axis = plane_config.get('axis', 'z')
        offset = plane_config.get('offset', 0)

        plane, _ = create_section_plane(point, normal)
        result = section_shape_by_plane(shape, plane)

        if result.get('success'):
            results.append({
                'axis': axis,
                'offset': offset,
                'edge_count': result['edge_count'],
                'shape': result['shape']
            })

    return {
        'polylines': results,
        'section_count': len(results)
    }