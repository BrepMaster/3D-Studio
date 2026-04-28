import os
import zipfile
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def read_3mf_file_debug(filepath: str):
    """Read 3MF file using trimesh library"""
    file_size = os.path.getsize(filepath)
    logger.info(f"Reading 3MF file: {filepath}, size: {file_size} bytes")

    try:
        import trimesh
        
        mesh = trimesh.load(filepath, file_type='3mf')
        
        logger.info(f"Loaded mesh with trimesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        
        if len(mesh.vertices) == 0:
            raise ValueError("3MF file contains no valid vertex data")

        if len(mesh.vertices) > 100000 or len(mesh.faces) > 100000:
            raise ValueError(f"3MF file too large ({len(mesh.vertices)} vertices, {len(mesh.faces)} faces), cannot process")

        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
        from OCC.Core.BRep import BRep_Builder
        from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Shape
        from OCC.Core.gp import gp_Pnt

        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)

        vertices = mesh.vertices.tolist()
        faces = mesh.faces.tolist()

        for face in faces:
            if len(face) < 3:
                continue

            try:
                polygon_points = []
                for idx in face[:3]:
                    if idx >= 0 and idx < len(vertices):
                        v = vertices[idx]
                        polygon_points.append(gp_Pnt(v[0], v[1], v[2]))

                if len(polygon_points) >= 3:
                    poly_builder = BRepBuilderAPI_MakePolygon()
                    for pnt in polygon_points:
                        poly_builder.Add(pnt)
                    poly_builder.Close()
                    if poly_builder.IsDone():
                        face_builder = BRepBuilderAPI_MakeFace(poly_builder.Wire())
                        if face_builder.IsDone():
                            builder.Add(compound, face_builder.Shape())
            except Exception as e:
                logger.warning(f"Error processing face: {e}")
                continue

        if compound.IsNull():
            raise ValueError("Unable to build geometry from 3MF file")

        logger.info("Successfully built geometry from 3MF file using trimesh")
        return compound

    except ImportError:
        logger.warning("trimesh not available, falling back to manual parsing")
        return read_3mf_manual(filepath)
    except Exception as e:
        logger.error(f"Failed to read 3MF file with trimesh: {e}")
        return read_3mf_manual(filepath)


def read_3mf_manual(filepath: str):
    """Manual 3MF file parsing as fallback"""
    file_size = os.path.getsize(filepath)
    logger.info(f"Reading 3MF file (manual): {filepath}, size: {file_size} bytes")

    try:
        vertices = []
        faces = []

        with zipfile.ZipFile(filepath, 'r') as zf:
            files = zf.namelist()
            logger.info(f"3MF archive contents ({len(files)} files):")
            for f in files:
                logger.info(f"  - {f}")
            
            model_file_path = None
            for f in files:
                if f.lower().endswith('.model'):
                    model_file_path = f
                    break
            if not model_file_path:
                for f in files:
                    if '3D' in f or 'model' in f.lower():
                        model_file_path = f
                        break
            
            if not model_file_path:
                raise ValueError(f"3MF file does not contain a model file. Contents: {files}")
            
            logger.info(f"Selected model file: {model_file_path}")
            
            with zf.open(model_file_path) as model_file:
                raw_content = model_file.read()
                logger.info(f"Model file raw size: {len(raw_content)} bytes")
                
                try:
                    content = raw_content.decode('utf-8')
                    logger.info("File decoded as UTF-8")
                except UnicodeDecodeError:
                    try:
                        content = raw_content.decode('utf-16')
                        logger.info("File decoded as UTF-16")
                    except:
                        content = raw_content.decode('utf-8', errors='replace')
                        logger.info("File decoded as UTF-8 with replacement")
                
                logger.info(f"First 1000 chars of model file:\n{content[:1000]}")
                
                tree = ET.ElementTree(ET.fromstring(content))
                root = tree.getroot()
                
                logger.info(f"Root tag: {root.tag}")
                logger.info(f"Root attributes: {root.attrib}")
                
                all_elements = []
                for elem in root.iter():
                    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    if tag not in all_elements:
                        all_elements.append(tag)
                logger.info(f"Unique element tags found: {all_elements}")
                
                found_vertices = False
                
                for elem in root.iter():
                    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    if tag == 'mesh':
                        logger.info("Found mesh element via iteration")
                        for child in elem.iter():
                            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                            if child_tag == 'vertex':
                                if 'x' in child.attrib and 'y' in child.attrib and 'z' in child.attrib:
                                    x = float(child.get('x'))
                                    y = float(child.get('y'))
                                    z = float(child.get('z'))
                                    vertices.append((x, y, z))
                                    found_vertices = True
                            elif child_tag == 'triangle':
                                if 'v1' in child.attrib and 'v2' in child.attrib and 'v3' in child.attrib:
                                    v1 = int(child.get('v1'))
                                    v2 = int(child.get('v2'))
                                    v3 = int(child.get('v3'))
                                    faces.append((v1, v2, v3))
                logger.info(f"After direct iteration: {len(vertices)} vertices, {len(faces)} faces")

        logger.info(f"FINAL - Total vertices found: {len(vertices)}, total faces found: {len(faces)}")
        
        if not vertices:
            raise ValueError("3MF file contains no valid vertex data")

        logger.info(f"Parsed {len(vertices)} vertices, {len(faces)} faces")

        if len(vertices) > 100000 or len(faces) > 100000:
            raise ValueError(f"3MF file too large ({len(vertices)} vertices, {len(faces)} faces), cannot process")

        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
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
                    if idx >= 0 and idx < len(vertices):
                        v = vertices[idx]
                        polygon_points.append(gp_Pnt(v[0], v[1], v[2]))

                if len(polygon_points) >= 3:
                    poly_builder = BRepBuilderAPI_MakePolygon()
                    for pnt in polygon_points:
                        poly_builder.Add(pnt)
                    poly_builder.Close()
                    if poly_builder.IsDone():
                        face_builder = BRepBuilderAPI_MakeFace(poly_builder.Wire())
                        if face_builder.IsDone():
                            builder.Add(compound, face_builder.Shape())
            except Exception as e:
                logger.warning(f"Error processing face: {e}")
                continue

        if compound.IsNull():
            raise ValueError("Unable to build geometry from 3MF file")

        logger.info("Successfully built geometry from 3MF file (manual)")
        return compound

    except zipfile.BadZipFile:
        raise ValueError("Invalid 3MF file: not a valid ZIP archive")
    except ET.ParseError as e:
        raise ValueError(f"Invalid 3MF file: XML parse error - {str(e)}")
    except Exception as e:
        logger.error(f"Failed to read 3MF file (manual): {e}")
        raise ValueError(f"Failed to read 3MF file: {str(e)}")
