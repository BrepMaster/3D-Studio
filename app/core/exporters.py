"""3D model file export module

Responsible for exporting PythonOCC geometry shapes to various 3D model file formats.
"""

import os
import gc
from typing import Optional, Tuple
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh

from app.config import get_logger

logger = get_logger()


def get_output_format_info(output_format: str) -> Tuple[str, str]:
    """Get output format information"""
    format_info = {
        'stl': ('.stl', 'application/sla'),
        'obj': ('.obj', 'text/plain'),
        'gltf': ('.gltf', 'model/gltf+json'),
        'step': ('.step', 'application/step'),
        'igs': ('.igs', 'application/iges')
    }
    return format_info.get(output_format, ('.stl', 'application/sla'))


def shape_to_stl(
    shape,
    output_path: str,
    linear_deflection: float = 0.1,
    angular_deflection: float = 0.5
) -> str:
    """Export geometry shape to STL file"""
    if shape.IsNull():
        raise Exception("Shape is null")

    mesh = None
    writer = None

    try:
        mesh = BRepMesh_IncrementalMesh(shape, linear_deflection, False, angular_deflection)
        mesh.Perform()
        
        if not mesh.IsDone():
            logger.warning("Initial meshing failed, trying finer deflection")
            del mesh
            mesh = BRepMesh_IncrementalMesh(shape, linear_deflection/2, False, angular_deflection/2)
            mesh.Perform()
            if not mesh.IsDone():
                raise Exception("Meshing completely failed")

        writer = StlAPI_Writer()
        writer.SetASCIIMode(True)
        writer.Write(shape, output_path)

        if not os.path.exists(output_path):
            raise Exception("Generated STL file does not exist")
        if os.path.getsize(output_path) == 0:
            raise Exception("Generated STL file is empty")

        return output_path
    finally:
        del mesh, writer
        gc.collect()


def shape_to_obj(
    shape,
    output_path: str,
    linear_deflection: float = 0.1,
    angular_deflection: float = 0.5
) -> str:
    """Export geometry shape to OBJ file"""
    if shape.IsNull():
        raise Exception("Shape is null")

    mesh = None
    writer = None

    try:
        mesh = BRepMesh_IncrementalMesh(shape, linear_deflection, False, angular_deflection)
        mesh.Perform()
        
        if not mesh.IsDone():
            logger.warning("Meshing before OBJ export failed, trying finer parameters")
            del mesh
            mesh = BRepMesh_IncrementalMesh(shape, linear_deflection/2, False, angular_deflection/2)
            mesh.Perform()
            if not mesh.IsDone():
                logger.error("Meshing failed, cannot export OBJ")
                stl_path = output_path.replace('.obj', '.stl')
                return shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)

        try:
            from OCC.Core.OBJControl import OBJControl_Writer
            writer = OBJControl_Writer()
            writer.SetFormat(OBJControl_Writer.OBJFormat_ASCII)
            if writer.Transfer(shape) == 0:
                raise Exception("OBJControl_Writer.Transfer failed")
            writer.Write(output_path)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                with open(output_path, 'r') as f:
                    content = f.read()
                if 'v ' in content:
                    return output_path
                else:
                    logger.warning("OBJ file has no vertex data, trying STL to OBJ conversion")
        except Exception as e:
            logger.error(f"OBJControl_Writer failed: {e}")

        stl_path = output_path.replace('.obj', '.stl')
        shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)

        if os.path.exists(stl_path) and os.path.getsize(stl_path) > 0:
            try:
                vertices = []
                faces = []
                current_face = []

                with open(stl_path, 'r') as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if line.startswith('vertex'):
                        parts = line.split()
                        if len(parts) == 4:
                            vertices.append(f"v {parts[1]} {parts[2]} {parts[3]}")
                            current_face.append(len(vertices))
                    elif line.startswith('endfacet'):
                        if len(current_face) == 3:
                            faces.append(f"f {current_face[0]} {current_face[1]} {current_face[2]}")
                        current_face = []

                with open(output_path, 'w') as f:
                    f.write('# OBJ file generated from STL\n')
                    for vertex in vertices:
                        f.write(vertex + '\n')
                    for face in faces:
                        f.write(face + '\n')

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    with open(output_path, 'r') as f:
                        content = f.read()
                    if 'v ' in content:
                        logger.info("Successfully converted from STL to OBJ")
                        return output_path
            except Exception as e:
                logger.error(f"STL to OBJ conversion failed: {e}")

        stl_path = output_path.replace('.obj', '.stl')
        return shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)
    finally:
        del mesh, writer
        gc.collect()


def shape_to_gltf(
    shape,
    output_path: str,
    linear_deflection: float = 0.1,
    angular_deflection: float = 0.5
) -> str:
    """Export geometry shape to GLTF file"""
    if shape.IsNull():
        raise Exception("Shape is null")

    writer = None

    try:
        from OCC.Core.GLTFControl import GLTFControl_Writer
        writer = GLTFControl_Writer()
        writer.Transfer(shape)
        writer.Write(output_path)

        if not os.path.exists(output_path):
            raise Exception("Generated GLTF file does not exist")
        if os.path.getsize(output_path) == 0:
            raise Exception("Generated GLTF file is empty")

        return output_path
    except Exception as e:
        logger.error(f"GLTF export failed: {e}")
        stl_path = output_path.replace('.gltf', '.stl')
        return shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)
    finally:
        del writer
        gc.collect()


def shape_to_step(shape, output_path: str) -> str:
    """Export geometry shape to STEP file"""
    if shape.IsNull():
        raise Exception("Shape is null")

    writer = None

    try:
        from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
        from OCC.Core.IFSelect import IFSelect_RetDone
        from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound
        from OCC.Core.BRepTools import breptools_Write

        brep_path = output_path.replace('.step', '.brep')
        try:
            breptools_Write(shape, brep_path)
            if os.path.exists(brep_path):
                logger.info(f"Successfully exported BRep file: {brep_path}, size: {os.path.getsize(brep_path)} bytes")
            else:
                logger.warning(f"BRep file not generated: {brep_path}")
        except Exception as e:
            logger.warning(f"BRep export failed: {e}")

        writer = STEPControl_Writer()

        if shape.ShapeType() == TopoDS_Compound:
            logger.info("Processing compound shape")

        transfer_result = writer.Transfer(shape, STEPControl_AsIs)
        logger.info(f"Transfer result: {transfer_result}")
        if transfer_result == 0:
            raise Exception("Shape transfer failed")

        status = writer.Write(output_path)
        logger.info(f"Write status: {status}, IFSelect_RetDone: {IFSelect_RetDone}")

        if status != IFSelect_RetDone:
            raise Exception(f"STEP export failed with status code: {status}")

        if not os.path.exists(output_path):
            raise Exception("Generated STEP file does not exist")

        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception("Generated STEP file is empty")

        try:
            with open(output_path, 'r') as f:
                content = f.read()

            if 'ISO-10303-21' not in content:
                raise Exception("Generated STEP file does not contain valid STEP data")

            logger.info(f"Successfully exported STEP file: {output_path}, size: {file_size} bytes")
        except Exception as e:
            logger.error(f"STEP file content check failed: {e}")
            raise

        return output_path
    except Exception as e:
        logger.error(f"STEP export failed: {e}")
        stl_path = output_path.replace('.step', '.stl')
        return shape_to_stl(shape, stl_path)
    finally:
        del writer
        gc.collect()


def shape_to_iges(shape, output_path: str) -> str:
    """Export geometry shape to IGES file"""
    if shape.IsNull():
        raise Exception("Shape is null")

    writer = None

    try:
        from OCC.Core.IGESControl import IGESControl_Writer, IGESControl_AsIs
        writer = IGESControl_Writer()
        writer.Transfer(shape, IGESControl_AsIs)
        status = writer.Write(output_path)
        if status <= 0:
            raise Exception("IGES export failed")

        if not os.path.exists(output_path):
            raise Exception("Generated IGES file does not exist")
        if os.path.getsize(output_path) == 0:
            raise Exception("Generated IGES file is empty")

        return output_path
    except Exception as e:
        logger.error(f"IGES export failed: {e}")
        stl_path = output_path.replace('.igs', '.stl')
        return shape_to_stl(shape, stl_path)
    finally:
        del writer
        gc.collect()