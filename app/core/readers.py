"""3D model file reader module

Responsible for reading various 3D model file formats, including STEP, IGES, STL, and OBJ files.
"""

import os
import gc
import time
from typing import Dict, Any, Optional, List, Tuple
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.IGESControl import IGESControl_Reader
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add

from app.config import get_logger
from app.utils import format_file_size

logger = get_logger()


def read_step_file(filepath: str):
    """Read STEP file"""
    file_size = os.path.getsize(filepath)
    logger.info(f"Reading STEP file: {filepath}, size: {format_file_size(file_size)}")

    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024
    logger.info(f"Initial memory usage: {initial_memory:.2f} MB")

    reader = None
    shape = None

    try:
        reader = STEPControl_Reader()
        status = reader.ReadFile(filepath)
        if status != IFSelect_RetDone:
            raise ValueError(f"Failed to read STEP file: status code {status}")
        if reader.TransferRoots() == 0:
            raise ValueError("STEP file contains no valid geometry")
        shape = reader.OneShape()

        if shape.IsNull():
            raise ValueError("STEP file conversion resulted in empty shape")

        final_memory = process.memory_info().rss / 1024 / 1024
        logger.info(f"Final memory usage: {final_memory:.2f} MB, memory increase: {final_memory - initial_memory:.2f} MB")

        return shape
    except ValueError as e:
        logger.error(f"Failed to read STEP file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unknown error reading STEP file: {e}")
        raise
    finally:
        del reader
        gc.collect()
        time.sleep(0.1)


def read_iges_file(filepath: str):
    """Read IGES file"""
    file_size = os.path.getsize(filepath)
    logger.info(f"Reading IGES file: {filepath}, size: {format_file_size(file_size)}")

    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024
    logger.info(f"Initial memory usage: {initial_memory:.2f} MB")

    reader = None
    shape = None

    try:
        reader = IGESControl_Reader()
        status = reader.ReadFile(filepath)
        if status <= 0:
            raise ValueError(f"Failed to read IGES file: status code {status}")
        if reader.TransferRoots() == 0:
            raise ValueError("IGES file contains no valid geometry")
        shape = reader.OneShape()
        if shape.IsNull():
            raise ValueError("IGES file conversion resulted in empty shape")

        final_memory = process.memory_info().rss / 1024 / 1024
        logger.info(f"Final memory usage: {final_memory:.2f} MB, memory increase: {final_memory - initial_memory:.2f} MB")

        return shape
    except ValueError as e:
        logger.error(f"Failed to read IGES file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unknown error reading IGES file: {e}")
        raise
    finally:
        del reader
        gc.collect()
        time.sleep(0.1)


def read_stl_file(filepath: str):
    """Read STL file"""
    file_size = os.path.getsize(filepath)
    logger.info(f"Reading STL file: {filepath}, size: {format_file_size(file_size)}")

    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024
    logger.info(f"Initial memory usage: {initial_memory:.2f} MB")

    reader = None
    shape = None
    mesh = None
    sewer = None
    fixer = None
    reshaper = None

    try:
        from OCC.Core.StlAPI import StlAPI_Reader
        from OCC.Core.TopoDS import TopoDS_Shape

        reader = StlAPI_Reader()
        shape = TopoDS_Shape()
        status = reader.Read(shape, filepath)

        if not status:
            raise ValueError("Failed to read STL file")
        if shape.IsNull():
            raise ValueError("STL file conversion resulted in empty shape")

        logger.info("Successfully read STL file")

        final_memory = process.memory_info().rss / 1024 / 1024
        logger.info(f"Final memory usage: {final_memory:.2f} MB, memory increase: {final_memory - initial_memory:.2f} MB")

        return shape
    except ValueError as e:
        logger.error(f"Failed to read STL file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unknown error reading STL file: {e}")
        raise
    finally:
        del mesh, sewer, fixer, reshaper, reader
        gc.collect()
        time.sleep(0.05)


def read_obj_file(filepath: str):
    """Read OBJ file"""
    file_size = os.path.getsize(filepath)
    logger.info(f"Reading OBJ file: {filepath}, size: {format_file_size(file_size)}")

    try:
        vertices = []
        faces = []

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith('v '):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                            vertices.append((x, y, z))
                        except ValueError:
                            continue
                elif line.startswith('f '):
                    parts = line.split()
                    if len(parts) >= 4:
                        face_indices = []
                        for part in parts[1:]:
                            try:
                                idx = int(part.split('/')[0])
                                face_indices.append(idx)
                            except ValueError:
                                continue
                        if len(face_indices) >= 3:
                            faces.append(face_indices)

        if not vertices:
            raise ValueError("OBJ file contains no valid vertex data")

        logger.info(f"Parsed {len(vertices)} vertices, {len(faces)} faces")

        if len(vertices) > 100000 or len(faces) > 100000:
            raise ValueError(f"OBJ file too large ({len(vertices)} vertices, {len(faces)} faces), cannot process")

        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon3D, BRepBuilderAPI_MakeFace
        from OCC.Core.BRep import BRep_Builder
        from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Shape
        from OCC.Core.gp import gp_Pnt

        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)

        for face in faces:
            if len(face) < 3:
                continue

            try:
                polygon_points = []
                for idx in face[:3]:
                    if idx > 0 and idx <= len(vertices):
                        v = vertices[idx - 1]
                        polygon_points.append(gp_Pnt(v[0], v[1], v[2]))

                if len(polygon_points) >= 3:
                    poly_builder = BRepBuilderAPI_MakePolygon3D(polygon_points)
                    if poly_builder.IsDone():
                        face_builder = BRepBuilderAPI_MakeFace(poly_builder.Shape())
                        if face_builder.IsDone():
                            builder.Add(compound, face_builder.Shape())
            except Exception as e:
                logger.warning(f"Error processing face: {e}")
                continue

        if compound.IsNull():
            raise ValueError("Unable to build geometry from OBJ file")

        logger.info("Successfully built geometry from OBJ file")
        return compound

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to read OBJ file: {e}")
        raise ValueError(f"Failed to read OBJ file: {str(e)}")


def read_3mf_file(filepath: str):
    """Read 3MF file"""
    from .readers_3mf import read_3mf_file_debug
    return read_3mf_file_debug(filepath)


def read_file_by_extension(file_path: str, ext: str):
    """Read 3D model file based on file extension"""
    try:
        if ext in ['step', 'stp']:
            return read_step_file(file_path)
        elif ext in ['igs', 'iges']:
            return read_iges_file(file_path)
        elif ext in ['stl']:
            return read_stl_file(file_path)
        elif ext in ['obj']:
            return read_obj_file(file_path)
        elif ext in ['3mf']:
            return read_3mf_file(file_path)
        else:
            raise Exception(f"Unsupported file type: {ext}")
    finally:
        gc.collect()


def get_shape_bounding_box(shape) -> Dict[str, Any]:
    """Get bounding box of shape"""
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    return {
        'min': [xmin, ymin, zmin],
        'max': [xmax, ymax, zmax],
        'size': [xmax-xmin, ymax-ymin, zmax-zmin]
    }


def get_shape_topology_info(shape) -> Dict[str, Any]:
    """Get topology information of shape"""
    face_count = edge_count = vertex_count = 0
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face_count += 1
        explorer.Next()
    explorer.Init(shape, TopAbs_EDGE)
    while explorer.More():
        edge_count += 1
        explorer.Next()
    explorer.Init(shape, TopAbs_VERTEX)
    while explorer.More():
        vertex_count += 1
        explorer.Next()
    return {
        'faces': face_count,
        'edges': edge_count,
        'vertices': vertex_count,
        'bounding_box': get_shape_bounding_box(shape)
    }


def get_shape_physical_properties(shape) -> Dict[str, Any]:
    """Get physical properties of shape"""
    try:
        from OCC.Core.BRepGProp import brepgprop
        from OCC.Core.GProp import GProp_GProps

        props = GProp_GProps()
        brepgprop.VolumeProperties(shape, props)

        volume = props.Mass()

        center_of_mass = props.CentreOfMass()
        com = [center_of_mass.X(), center_of_mass.Y(), center_of_mass.Z()]

        surface_props = GProp_GProps()
        brepgprop.SurfaceProperties(shape, surface_props)
        surface_area = surface_props.Mass()

        inertia_tensor = props.MatrixOfInertia()
        inertia = {
            'ixx': inertia_tensor.Value(1, 1),
            'iyy': inertia_tensor.Value(2, 2),
            'izz': inertia_tensor.Value(3, 3),
            'ixy': inertia_tensor.Value(1, 2),
            'iyz': inertia_tensor.Value(2, 3),
            'izx': inertia_tensor.Value(3, 1)
        }

        return {
            'volume': volume,
            'surface_area': surface_area,
            'center_of_mass': com,
            'inertia': inertia
        }
    except Exception as e:
        logger.error(f'Failed to calculate physical properties: {e}')
        return {
            'volume': 0.0,
            'surface_area': 0.0,
            'center_of_mass': [0.0, 0.0, 0.0],
            'inertia': {
                'ixx': 0.0, 'iyy': 0.0, 'izz': 0.0,
                'ixy': 0.0, 'iyz': 0.0, 'izx': 0.0
            }
        }


def get_shape_quality_report(shape) -> Dict[str, Any]:
    """Get quality report of shape"""
    try:
        topology_info = get_shape_topology_info(shape)
        physical_props = get_shape_physical_properties(shape)

        face_count = topology_info['faces']
        edge_count = topology_info['edges']
        vertex_count = topology_info['vertices']
        volume = physical_props['volume']
        surface_area = physical_props['surface_area']

        compactness = 0.0
        if volume > 0:
            compactness = surface_area / volume

        quality_score = 0
        if face_count < 10000 and edge_count < 30000:
            quality_score += 30
        elif face_count < 50000 and edge_count < 150000:
            quality_score += 20
        else:
            quality_score += 10

        if volume > 0:
            quality_score += 20

        if surface_area > 0:
            quality_score += 20

        if compactness > 0 and compactness < 1000:
            quality_score += 30
        elif compactness < 5000:
            quality_score += 20
        else:
            quality_score += 10

        report = {
            'topology': topology_info,
            'physical': physical_props,
            'compactness': compactness,
            'quality_score': quality_score,
            'quality_level': 'Excellent' if quality_score >= 90 else 'Good' if quality_score >= 70 else 'Fair' if quality_score >= 50 else 'Poor',
            'recommendations': []
        }

        if face_count > 50000:
            report['recommendations'].append('Model has many faces, consider simplification for better performance')

        if volume <= 0:
            report['recommendations'].append('Model volume is zero, may have geometric issues')

        if compactness > 5000:
            report['recommendations'].append('Model compactness is high, may have geometric issues')

        return report
    except Exception as e:
        logger.error(f'Failed to generate quality report: {e}')
        return {
            'topology': {},
            'physical': {},
            'compactness': 0.0,
            'quality_score': 0,
            'quality_level': 'Unknown',
            'recommendations': ['Unable to generate quality report']
        }


def get_model_info_quick(filepath: str) -> Dict[str, Any]:
    """Quickly get basic model information"""
    try:
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()

        format_type = ext[1:] if ext else 'unknown'

        bounding_box = None

        if ext in ['.step', '.stp']:
            try:
                reader = STEPControl_Reader()
                status = reader.ReadFile(filepath)
                if status == IFSelect_RetDone:
                    if reader.TransferRoots() > 0:
                        shape = reader.OneShape()
                        bounding_box = get_shape_bounding_box(shape)
                    del reader
            except Exception as e:
                logger.warning(f'Failed to quickly read STEP file: {e}')
        elif ext in ['.iges', '.igs']:
            try:
                reader = IGESControl_Reader()
                status = reader.ReadFile(filepath)
                if status > 0:
                    if reader.TransferRoots() > 0:
                        shape = reader.OneShape()
                        if not shape.IsNull():
                            bounding_box = get_shape_bounding_box(shape)
                    del reader
            except Exception as e:
                logger.warning(f'Failed to quickly read IGES file: {e}')
        elif ext in ['.stl']:
            try:
                from OCC.Core.StlAPI import StlAPI_Reader
                from OCC.Core.TopoDS import TopoDS_Shape
                reader = StlAPI_Reader()
                shape = TopoDS_Shape()
                status = reader.Read(shape, filepath)
                if status and not shape.IsNull():
                    bounding_box = get_shape_bounding_box(shape)
                del reader
            except Exception as e:
                logger.warning(f'Failed to quickly read STL file: {e}')
        elif ext in ['.obj']:
            try:
                min_x = min_y = min_z = float('inf')
                max_x = max_y = max_z = float('-inf')

                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('v '):
                            parts = line.split()
                            if len(parts) >= 4:
                                x = float(parts[1])
                                y = float(parts[2])
                                z = float(parts[3])
                                min_x = min(min_x, x)
                                min_y = min(min_y, y)
                                min_z = min(min_z, z)
                                max_x = max(max_x, x)
                                max_y = max(max_y, y)
                                max_z = max(max_z, z)

                if min_x != float('inf'):
                    bounding_box = {
                        'min': [min_x, min_y, min_z],
                        'max': [max_x, max_y, max_z],
                        'size': [max_x - min_x, max_y - min_y, max_z - min_z]
                    }
            except Exception as e:
                logger.warning(f'Failed to quickly read OBJ file: {e}')
        elif ext in ['.3mf']:
            try:
                import zipfile
                import xml.etree.ElementTree as ET

                min_x = min_y = min_z = float('inf')
                max_x = max_y = max_z = float('-inf')

                with zipfile.ZipFile(filepath, 'r') as zf:
                    with zf.open('3D/3dmodel.model') as model_file:
                        tree = ET.parse(model_file)
                        root = tree.getroot()

                        namespace = {'mf': 'http://schemas.microsoft.com/3dmanufacturing/core/2009/11'}

                        for vertex in root.findall('.//mf:vertex', namespace):
                            x = float(vertex.get('x'))
                            y = float(vertex.get('y'))
                            z = float(vertex.get('z'))
                            min_x = min(min_x, x)
                            min_y = min(min_y, y)
                            min_z = min(min_z, z)
                            max_x = max(max_x, x)
                            max_y = max(max_y, y)
                            max_z = max(max_z, z)

                if min_x != float('inf'):
                    bounding_box = {
                        'min': [min_x, min_y, min_z],
                        'max': [max_x, max_y, max_z],
                        'size': [max_x - min_x, max_y - min_y, max_z - min_z]
                    }
            except Exception as e:
                logger.warning(f'Failed to quickly read 3MF file: {e}')

        info = {
            'filename': filename,
            'format': format_type,
            'file_size': file_size,
            'file_size_formatted': format_file_size(file_size)
        }

        if bounding_box:
            info['bounding_box'] = bounding_box
            size = bounding_box['size']
            info['approximate_size'] = {
                'length': max(size),
                'width': sorted(size)[1],
                'height': min(size)
            }

        gc.collect()
        return info
    except Exception as e:
        logger.error(f'Failed to quickly get model info: {e}')
        return {
            'error': str(e),
            'filename': os.path.basename(filepath) if 'filepath' in locals() else 'unknown',
            'format': 'unknown',
            'file_size': 0,
            'file_size_formatted': '0 B'
        }