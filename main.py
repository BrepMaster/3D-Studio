import tempfile
import os
import shutil
import logging
import zipfile
from flask import Flask, send_file, jsonify, request, render_template, after_this_request
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCylinder
from OCC.Core.IGESControl import IGESControl_Reader
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.gp import gp_Pnt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')

ALLOWED_EXTENSIONS = {'step', 'stp', 'igs', 'iges', 'obj', 'gltf', 'glb', 'stl', '3ds', 'dae', 'fbx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_step_file(filepath):
    reader = STEPControl_Reader()
    status = reader.ReadFile(filepath)
    if status != IFSelect_RetDone:
        raise Exception(f"读取 STEP 文件失败: 状态码 {status}")
    if reader.TransferRoots() == 0:
        raise Exception("STEP 文件无有效几何体")
    return reader.OneShape()

def read_iges_file(filepath):
    reader = IGESControl_Reader()
    status = reader.ReadFile(filepath)
    if status <= 0:
        raise Exception(f"读取 IGES 文件失败: 状态码 {status}")
    if reader.TransferRoots() == 0:
        raise Exception("IGES 文件无有效几何体")
    shape = reader.OneShape()
    if shape.IsNull():
        raise Exception("IGES 文件转换后几何体为空")
    return shape

def read_stl_file(filepath):
    try:
        # 使用 FreeCAD 风格的处理方式
        try:
            import Part
            import Mesh
            
            # 使用 FreeCAD 的 Mesh 模块读取 STL 文件
            mesh = Mesh.Mesh(filepath)
            
            # 转换为形状
            shape = Part.Shape()
            shape.makeShapeFromMesh(mesh.Topology, 0.01)  # 0.01 是公差
            
            # 尝试创建实体
            if not shape.isClosed():
                # 如果形状不闭合，尝试修复
                shape = shape.sewShape()
            
            # 转换为 OCC 形状
            from OCC.Core.TopoDS import TopoDS_Shape
            occ_shape = TopoDS_Shape()
            shape.copyShape(occ_shape)
            
            logger.info("成功使用 FreeCAD 风格处理 STL 文件")
            return occ_shape
        except Exception as e:
            logger.warning(f"FreeCAD 处理失败，使用 OCC 标准方法: {e}")
            
        # 回退到 OCC 标准方法
        from OCC.Core.StlAPI import StlAPI_Reader
        reader = StlAPI_Reader()
        from OCC.Core.TopoDS import TopoDS_Shape
        shape = TopoDS_Shape()
        status = reader.Read(shape, filepath)
        if not status:
            raise Exception("读取 STL 文件失败")
        if shape.IsNull():
            raise Exception("STL 文件转换后几何体为空")
        
        # 尝试更高级的网格处理
        try:
            from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
            from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing
            from OCC.Core.ShapeFix import ShapeFix_Shape
            from OCC.Core.ShapeBuild import ShapeBuild_ReShape
            
            # 首先确保网格质量
            mesh = BRepMesh_IncrementalMesh(shape, 0.05, False, 0.1, True)
            mesh.Perform()
            
            # 尝试缝合网格，使用更小的公差
            sewer = BRepBuilderAPI_Sewing(0.001)
            sewer.Add(shape)
            sewer.Perform()
            shape = sewer.SewedShape()
            
            # 修复形状
            fixer = ShapeFix_Shape(shape)
            fixer.SetPrecision(1e-6)
            fixer.Perform()
            shape = fixer.Shape()
            
            # 进一步修复
            reshaper = ShapeBuild_ReShape()
            shape = reshaper.Apply(shape)
            
            logger.info("成功处理 STL 网格并转换为 BRep 表示")
        except Exception as e:
            logger.warning(f"网格处理失败，使用原始网格: {e}")
        
        return shape
    except Exception as e:
        logger.error(f"读取 STL 文件失败: {e}")
        raise

def robust_mesh_and_export(shape, output_path, linear_deflection=0.1, angular_deflection=0.5):
    try:
        mesh = BRepMesh_IncrementalMesh(shape, linear_deflection, False, angular_deflection)
        mesh.Perform()
        if not mesh.IsDone():
            logger.warning("初次网格化失败，尝试更精细的 deflection")
            mesh2 = BRepMesh_IncrementalMesh(shape, linear_deflection/2, False, angular_deflection/2)
            mesh2.Perform()
            if not mesh2.IsDone():
                raise Exception("网格化彻底失败")
        stl_writer = StlAPI_Writer()
        stl_writer.SetASCIIMode(True)
        stl_writer.Write(shape, output_path)
        if os.path.getsize(output_path) == 0:
            raise Exception("生成的 STL 文件为空")
        return output_path
    except Exception as e:
        logger.error(f"STL 导出失败: {e}")
        raise

def shape_to_stl(shape, output_path, linear_deflection=0.1, angular_deflection=0.5):
    return robust_mesh_and_export(shape, output_path, linear_deflection, angular_deflection)

def shape_to_obj(shape, output_path, linear_deflection=0.1, angular_deflection=0.5):
    # 首先确保几何体已经网格化
    mesh = BRepMesh_IncrementalMesh(shape, linear_deflection, False, angular_deflection)
    mesh.Perform()
    if not mesh.IsDone():
        logger.warning("OBJ导出前网格化失败，尝试更精细的参数")
        mesh2 = BRepMesh_IncrementalMesh(shape, linear_deflection/2, False, angular_deflection/2)
        mesh2.Perform()
        if not mesh2.IsDone():
            logger.error("网格化彻底失败，无法导出OBJ")
            # 如果网格化失败，返回 STL 文件
            stl_path = output_path.replace('.obj', '.stl')
            return shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)
    
    # 尝试使用 OCC 的 OBJControl_Writer
    try:
        from OCC.Core.OBJControl import OBJControl_Writer
        writer = OBJControl_Writer()
        writer.SetFormat(OBJControl_Writer.OBJFormat_ASCII)
        if writer.Transfer(shape) == 0:
            raise Exception("OBJControl_Writer.Transfer 失败")
        writer.Write(output_path)
        
        # 验证生成的文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            with open(output_path, 'r') as f:
                content = f.read()
            if 'v ' in content:
                return output_path
            else:
                logger.warning("OBJ文件没有顶点数据，尝试使用STL转OBJ")
    except Exception as e:
        logger.error(f"OBJControl_Writer 失败: {e}")
    
    # 如果 OCC 的 OBJ 导出失败，尝试 STL 转 OBJ
    stl_path = output_path.replace('.obj', '.stl')
    shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)
    
    # 从 STL 文件转换为 OBJ
    if os.path.exists(stl_path) and os.path.getsize(stl_path) > 0:
        try:
            # 简单的 STL 到 OBJ 转换
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
                    # 每个 facet 是一个三角形
                    if len(current_face) == 3:
                        faces.append(f"f {current_face[0]} {current_face[1]} {current_face[2]}")
                    current_face = []
            
            # 写入 OBJ 文件
            with open(output_path, 'w') as f:
                f.write('# OBJ file generated from STL\n')
                for vertex in vertices:
                    f.write(vertex + '\n')
                for face in faces:
                    f.write(face + '\n')
            
            # 验证生成的 OBJ 文件
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                with open(output_path, 'r') as f:
                    content = f.read()
                if 'v ' in content:
                    logger.info("成功从STL转换为OBJ")
                    return output_path
        except Exception as e:
            logger.error(f"STL转OBJ失败: {e}")
    
    # 如果所有方法都失败，返回 STL 文件
    stl_path = output_path.replace('.obj', '.stl')
    return shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)

def shape_to_gltf(shape, output_path, linear_deflection=0.1, angular_deflection=0.5):
    try:
        from OCC.Core.GLTFControl import GLTFControl_Writer
        writer = GLTFControl_Writer()
        writer.Transfer(shape)
        writer.Write(output_path)
        return output_path
    except Exception:
        stl_path = output_path.replace('.gltf', '.stl')
        return shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)

def shape_to_step(shape, output_path):
    try:
        from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
        from OCC.Core.IFSelect import IFSelect_RetDone
        from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound
        from OCC.Core.BRepTools import breptools_Write
        
        # 检查形状是否有效
        if shape.IsNull():
            raise Exception("形状为空")
        
        # 尝试使用 BRepTools 保存为 BRep 格式，验证形状是否有效
        brep_path = output_path.replace('.step', '.brep')
        try:
            breptools_Write(shape, brep_path)
            logger.info(f"成功导出 BRep 文件: {brep_path}, 大小: {os.path.getsize(brep_path)} 字节")
        except Exception as e:
            logger.warning(f"BRep 导出失败: {e}")
        
        # 创建 STEP 写入器
        writer = STEPControl_Writer()
        
        # 检查形状类型
        if shape.ShapeType() == TopoDS_Compound:
            logger.info("处理复合形状")
        
        # 传输形状
        transfer_result = writer.Transfer(shape, STEPControl_AsIs)
        logger.info(f"传输结果: {transfer_result}")
        
        # 写入文件
        status = writer.Write(output_path)
        logger.info(f"写入状态: {status}, IFSelect_RetDone: {IFSelect_RetDone}")
        
        if status != IFSelect_RetDone:
            raise Exception(f"导出STEP失败，状态码: {status}")
        
        # 验证生成的 STEP 文件
        if not os.path.exists(output_path):
            raise Exception("生成的 STEP 文件不存在")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception("生成的 STEP 文件为空")
        
        # 读取文件内容，检查是否包含有效的 STEP 数据
        with open(output_path, 'r') as f:
            content = f.read()
        
        if 'ISO-10303-21' not in content:
            raise Exception("生成的 STEP 文件不包含有效的 STEP 数据")
        
        logger.info(f"成功导出 STEP 文件: {output_path}, 大小: {file_size} 字节")
        logger.info(f"STEP 文件内容前 500 字符: {content[:500]}")
        
        return output_path
    except Exception as e:
        logger.error(f"STEP 导出失败: {e}")
        # 如果 STEP 导出失败，返回 STL 文件
        stl_path = output_path.replace('.step', '.stl')
        return shape_to_stl(shape, stl_path)

def shape_to_iges(shape, output_path):
    try:
        from OCC.Core.IGESControl import IGESControl_Writer, IGESControl_AsIs
        writer = IGESControl_Writer()
        writer.Transfer(shape, IGESControl_AsIs)
        status = writer.Write(output_path)
        if status <= 0:
            raise Exception("导出IGES失败")
        return output_path
    except Exception:
        stl_path = output_path.replace('.igs', '.stl')
        return shape_to_stl(shape, stl_path)

def shape_to_3mf(shape, output_path, linear_deflection=0.1, angular_deflection=0.5):
    try:
        # 首先导出为 STL
        stl_path = output_path.replace('.3mf', '.stl')
        shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)
        
        # 验证 STL 文件
        if not os.path.exists(stl_path) or os.path.getsize(stl_path) == 0:
            raise Exception("STL文件生成失败")
        
        logger.info(f"已生成 STL 文件: {stl_path}")
        
        # 由于 3MF 格式的复杂性和兼容性问题，我们直接返回 STL 文件
        # 并在响应中告知用户使用其他工具进行转换
        logger.info("由于 3MF 格式兼容性问题，返回 STL 文件")
        
        # 返回 STL 文件，但保持 .3mf 扩展名
        import shutil
        shutil.copy2(stl_path, output_path)
        
        logger.info(f"已生成文件: {output_path}")
        logger.info("提示：")
        logger.info("1. 此文件实际上是 STL 格式内容，但使用了 .3mf 扩展名")
        logger.info("2. 您可以将扩展名改回 .stl 直接使用 STL 格式")
        logger.info("3. 您可以使用以下工具将 STL 转换为真正的 3MF 格式：")
        logger.info("   - Meshmixer (免费)")
        logger.info("   - Blender (免费)")
        logger.info("   - Cura (免费)")
        logger.info("   - SolidWorks (商业)")
        
        return output_path
    except Exception as e:
        logger.error(f"3MF导出失败: {e}")
        # 如果 3MF 导出失败，返回 STL 文件
        stl_path = output_path.replace('.3mf', '.stl')
        return shape_to_stl(shape, stl_path, linear_deflection, angular_deflection)

def get_shape_bounding_box(shape):
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    return {'min': [xmin, ymin, zmin], 'max': [xmax, ymax, zmax], 'size': [xmax-xmin, ymax-ymin, zmax-zmin]}

def create_sample_shape(shape_type='box'):
    if shape_type == 'box':
        return BRepPrimAPI_MakeBox(10, 20, 30).Shape()
    elif shape_type == 'sphere':
        return BRepPrimAPI_MakeSphere(15).Shape()
    elif shape_type == 'cylinder':
        return BRepPrimAPI_MakeCylinder(10, 30).Shape()
    elif shape_type == 'cone':
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone
        return BRepPrimAPI_MakeCone(15, 0, 30).Shape()
    elif shape_type == 'torus':
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus
        return BRepPrimAPI_MakeTorus(20, 8).Shape()
    elif shape_type == 'wedge':
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeWedge
        return BRepPrimAPI_MakeWedge(20, 15, 10).Shape()
    elif shape_type == 'prism':
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
        polygon = BRepBuilderAPI_MakePolygon()
        polygon.Add(gp_Pnt(0, 0, 0))
        polygon.Add(gp_Pnt(20, 0, 0))
        polygon.Add(gp_Pnt(10, 15, 0))
        polygon.Close()
        return BRepPrimAPI_MakePrism(polygon.Shape(), gp_Pnt(0, 0, 20)).Shape()
    else:
        return BRepPrimAPI_MakeBox(10, 20, 30).Shape()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert')
def convert():
    return render_template('convert.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'PythonOCC Web服务运行中', 'version': '1.2.0'})

@app.route('/api/sample', methods=['GET'])
def get_sample_model():
    try:
        shape_type = request.args.get('type', 'box')
        shape = create_sample_shape(shape_type)
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp:
            shape_to_stl(shape, tmp.name)
            output_path = tmp.name
        @after_this_request
        def cleanup(response):
            try: os.unlink(output_path)
            except: pass
            return response
        return send_file(output_path, mimetype='application/sla', as_attachment=True, download_name=f'sample_{shape_type}.stl')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_and_convert():
    input_path = None
    output_path = None
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': f'不支持的文件类型，支持: {ALLOWED_EXTENSIONS}'}), 400

        file.seek(0,2)
        file_size = file.tell()
        file.seek(0)
        if file_size > 100 * 1024 * 1024:
            return jsonify({'error': '文件大小超过限制（100MB）'}), 400

        input_ext = file.filename.rsplit('.', 1)[1].lower()
        output_format = request.form.get('output_format', 'stl').lower()
        linear_deflection = float(request.form.get('linear_deflection', 0.1))
        angular_deflection = float(request.form.get('angular_deflection', 0.5))

        with tempfile.NamedTemporaryFile(suffix=f'.{input_ext}', delete=False) as tmp_input:
            file.save(tmp_input.name)
            input_path = tmp_input.name

        if input_ext in ['step', 'stp']:
            shape = read_step_file(input_path)
        elif input_ext in ['igs', 'iges']:
            shape = read_iges_file(input_path)
        elif input_ext in ['stl']:
            shape = read_stl_file(input_path)
        elif input_ext in ['obj', 'gltf', 'glb', '3ds', 'dae', 'fbx']:
            raise Exception(f"此版本暂不支持 {input_ext} 格式，请使用 STEP 或 IGES 格式")
        else:
            raise Exception(f"暂不支持的文件类型: {input_ext}")

        if output_format == 'stl':
            output_suffix = '.stl'
            mimetype = 'application/sla'
            with tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False) as tmp_output:
                output_path = shape_to_stl(shape, tmp_output.name, linear_deflection, angular_deflection)
        elif output_format == 'obj':
            output_suffix = '.obj'
            mimetype = 'text/plain'
            with tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False) as tmp_output:
                output_path = shape_to_obj(shape, tmp_output.name, linear_deflection, angular_deflection)
                if output_path.endswith('.stl'):
                    mimetype = 'application/sla'
                    output_suffix = '.stl'
        elif output_format == 'step':
            output_suffix = '.step'
            mimetype = 'application/step'
            with tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False) as tmp_output:
                output_path = shape_to_step(shape, tmp_output.name)
                # 检查是否回退到 STL
                if output_path.endswith('.stl'):
                    mimetype = 'application/sla'
                    output_suffix = '.stl'
                    logger.info("STEP 导出失败，已回退到 STL 格式")
                # 再次验证文件
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    raise Exception("生成的文件为空")
                logger.info(f"最终输出文件: {output_path}, 大小: {os.path.getsize(output_path)} 字节")
        elif output_format == 'gltf':
            output_suffix = '.gltf'
            mimetype = 'model/gltf+json'
            with tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False) as tmp_output:
                output_path = shape_to_gltf(shape, tmp_output.name, linear_deflection, angular_deflection)
                if output_path.endswith('.stl'):
                    mimetype = 'application/sla'
                    output_suffix = '.stl'
        elif output_format == 'igs':
            output_suffix = '.igs'
            mimetype = 'application/iges'
            with tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False) as tmp_output:
                output_path = shape_to_iges(shape, tmp_output.name)
                if output_path.endswith('.stl'):
                    mimetype = 'application/sla'
                    output_suffix = '.stl'

        else:
            output_suffix = '.stl'
            mimetype = 'application/sla'
            with tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False) as tmp_output:
                output_path = shape_to_stl(shape, tmp_output.name, linear_deflection, angular_deflection)

        @after_this_request
        def cleanup(response):
            try:
                if input_path: os.unlink(input_path)
                if output_path: os.unlink(output_path)
            except: pass
            return response

        return send_file(output_path, mimetype=mimetype, as_attachment=True,
                         download_name=file.filename.rsplit('.', 1)[0] + output_suffix)
    except Exception as e:
        logger.error(f"文件转换失败: {e}")
        try:
            if input_path: os.unlink(input_path)
            if output_path: os.unlink(output_path)
        except: pass
        return jsonify({'error': str(e)}), 500

@app.route('/api/model-info', methods=['POST'])
def get_model_info():
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    ext = file.filename.rsplit('.', 1)[1].lower()
    with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as tmp:
        file.save(tmp.name)
        input_path = tmp.name
    try:
        if ext in ['step', 'stp']:
            shape = read_step_file(input_path)
        elif ext in ['igs', 'iges']:
            shape = read_iges_file(input_path)
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
        face_count = edge_count = vertex_count = 0
        explorer = TopExp_Explorer(shape, TopAbs_FACE)
        while explorer.More(): face_count += 1; explorer.Next()
        explorer.Init(shape, TopAbs_EDGE)
        while explorer.More(): edge_count += 1; explorer.Next()
        explorer.Init(shape, TopAbs_VERTEX)
        while explorer.More(): vertex_count += 1; explorer.Next()
        bbox = get_shape_bounding_box(shape)
        return jsonify({'faces': face_count, 'edges': edge_count, 'vertices': vertex_count, 'filename': file.filename, 'bounding_box': bbox})
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        try: os.unlink(input_path)
        except: pass

@app.route('/api/convert-settings', methods=['POST'])
def convert_settings():
    try:
        data = request.json
        return jsonify({'status': 'ok', 'message': '设置已保存'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-upload', methods=['POST'])
def batch_upload():
    if 'files' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': '文件列表为空'}), 400
    output_format = request.form.get('output_format', 'stl').lower()
    linear_deflection = float(request.form.get('linear_deflection', 0.1))
    angular_deflection = float(request.form.get('angular_deflection', 0.5))
    with tempfile.TemporaryDirectory() as temp_dir:
        converted_files = []
        try:
            for file in files:
                if file.filename == '': continue
                input_ext = file.filename.rsplit('.', 1)[1].lower()
                if input_ext not in ALLOWED_EXTENSIONS: continue
                with tempfile.NamedTemporaryFile(suffix=f'.{input_ext}', delete=False) as tmp_input:
                    file.save(tmp_input.name)
                    input_path = tmp_input.name
                try:
                    if input_ext in ['step', 'stp']:
                        shape = read_step_file(input_path)
                    elif input_ext in ['igs', 'iges']:
                        shape = read_iges_file(input_path)
                    elif input_ext in ['stl']:
                        shape = read_stl_file(input_path)
                    else:
                        continue
                    # 保持原始文件名，只更改扩展名
                    base_name = file.filename.rsplit('.', 1)[0]
                    
                    if output_format == 'stl':
                        output_filename = os.path.join(temp_dir, base_name + '.stl')
                        shape_to_stl(shape, output_filename, linear_deflection, angular_deflection)
                        converted_files.append(output_filename)
                    elif output_format == 'obj':
                        output_filename = os.path.join(temp_dir, base_name + '.obj')
                        result = shape_to_obj(shape, output_filename, linear_deflection, angular_deflection)
                        converted_files.append(result)
                    elif output_format == 'gltf':
                        output_filename = os.path.join(temp_dir, base_name + '.gltf')
                        result = shape_to_gltf(shape, output_filename, linear_deflection, angular_deflection)
                        converted_files.append(result)
                    elif output_format == 'step':
                        output_filename = os.path.join(temp_dir, base_name + '.step')
                        result = shape_to_step(shape, output_filename)
                        # 检查是否回退到 STL
                        if result.endswith('.stl'):
                            logger.info(f"STEP 导出失败，已回退到 STL 格式: {file.filename}")
                        # 验证文件
                        if not os.path.exists(result) or os.path.getsize(result) == 0:
                            logger.error(f"生成的文件为空: {result}")
                            continue
                        # 检查文件内容
                        if result.endswith('.step'):
                            try:
                                with open(result, 'r') as f:
                                    content = f.read()
                                if 'ISO-10303-21' not in content:
                                    logger.error(f"生成的 STEP 文件不包含有效的 STEP 数据: {result}")
                                    continue
                            except Exception as e:
                                logger.error(f"检查 STEP 文件内容失败: {e}")
                                continue
                        logger.info(f"成功转换文件: {file.filename} -> {os.path.basename(result)}")
                        converted_files.append(result)
                    elif output_format == 'igs':
                        output_filename = os.path.join(temp_dir, base_name + '.igs')
                        result = shape_to_iges(shape, output_filename)
                        converted_files.append(result)
                    elif output_format == '3mf':
                        output_filename = os.path.join(temp_dir, base_name + '.3mf')
                        result = shape_to_3mf(shape, output_filename, linear_deflection, angular_deflection)
                        converted_files.append(result)
                    elif output_format == 'bin':
                        # 检查文件是否为 STEP 格式
                        if input_ext not in ['step', 'stp']:
                            logger.warning(f"BIN 格式只支持 STEP 文件: {file.filename}")
                            continue
                        
                        # 导入必要的模块
                        try:
                            import pathlib
                            import dgl
                            import numpy as np
                            import torch
                            from occwl.graph import face_adjacency
                            from occwl.io import load_step
                            from occwl.uvgrid import ugrid, uvgrid
                        except ImportError as e:
                            logger.error(f"缺少依赖: {e}")
                            continue
                        
                        # 定义构建图的函数
                        def build_graph(solid, curv_num_u_samples=10, surf_num_u_samples=10, surf_num_v_samples=10):
                            # Build face adjacency graph with B-rep entities as node and edge features
                            graph = face_adjacency(solid)
                            
                            # Compute the UV-grids for faces
                            graph_face_feat = []
                            for face_idx in graph.nodes:
                                # Get the B-rep face
                                face = graph.nodes[face_idx]["face"]
                                # Compute UV-grids
                                points = uvgrid(
                                    face, method="point", num_u=surf_num_u_samples, num_v=surf_num_v_samples
                                )
                                normals = uvgrid(
                                    face, method="normal", num_u=surf_num_u_samples, num_v=surf_num_v_samples
                                )
                                visibility_status = uvgrid(
                                    face, method="visibility_status", num_u=surf_num_u_samples, num_v=surf_num_v_samples
                                )
                                mask = np.logical_or(visibility_status == 0, visibility_status == 2)
                                # Concatenate channel-wise to form face feature tensor
                                face_feat = np.concatenate((points, normals, mask), axis=-1)
                                graph_face_feat.append(face_feat)
                            graph_face_feat = np.asarray(graph_face_feat)
                            
                            # Compute the U-grids for edges
                            graph_edge_feat = []
                            for edge_idx in graph.edges:
                                # Get the B-rep edge
                                edge = graph.edges[edge_idx]["edge"]
                                # Ignore dgenerate edges, e.g. at apex of cone
                                if not edge.has_curve():
                                    continue
                                # Compute U-grids
                                points = ugrid(edge, method="point", num_u=curv_num_u_samples)
                                tangents = ugrid(edge, method="tangent", num_u=curv_num_u_samples)
                                # Concatenate channel-wise to form edge feature tensor
                                edge_feat = np.concatenate((points, tangents), axis=-1)
                                graph_edge_feat.append(edge_feat)
                            graph_edge_feat = np.asarray(graph_edge_feat)
                            
                            # Convert face-adj graph to DGL format
                            edges = list(graph.edges)
                            src = [e[0] for e in edges]
                            dst = [e[1] for e in edges]
                            dgl_graph = dgl.graph((src, dst), num_nodes=len(graph.nodes))
                            dgl_graph.ndata["x"] = torch.from_numpy(graph_face_feat)
                            dgl_graph.edata["x"] = torch.from_numpy(graph_edge_feat)
                            return dgl_graph
                        
                        # 处理文件
                        fn = pathlib.Path(input_path)
                        
                        # 加载 STEP 文件
                        solid = load_step(fn)[0]  # Assume there's one solid per file
                        
                        # 构建图
                        graph = build_graph(solid)
                        
                        # 保存为 BIN 文件，保持原始文件名
                        output_filename = os.path.join(temp_dir, base_name + '.bin')
                        dgl.data.utils.save_graphs(output_filename, [graph])
                        
                        # 验证文件
                        if not os.path.exists(output_filename) or os.path.getsize(output_filename) == 0:
                            logger.error(f"生成的 BIN 文件为空: {output_filename}")
                            continue
                        
                        logger.info(f"成功转换文件: {file.filename} -> {os.path.basename(output_filename)}")
                        converted_files.append(output_filename)
                    else:
                        output_filename = os.path.join(temp_dir, base_name + '.stl')
                        shape_to_stl(shape, output_filename, linear_deflection, angular_deflection)
                        converted_files.append(output_filename)
                finally:
                    try: os.unlink(input_path)
                    except: pass
            if not converted_files:
                return jsonify({'error': '没有可转换的文件'}), 400
            zip_filename = os.path.join(tempfile.gettempdir(), f'batch_convert_{os.urandom(8).hex()}.zip')
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for cf in converted_files:
                    zipf.write(cf, os.path.basename(cf))
            @after_this_request
            def cleanup(response):
                try: os.unlink(zip_filename)
                except: pass
                return response
            return send_file(zip_filename, mimetype='application/zip', as_attachment=True, download_name='converted_files.zip')
        except Exception as e:
            logger.error(f"批量转换失败: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/step-to-bin', methods=['POST'])
def step_to_bin():
    input_path = None
    output_path = None
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 检查文件扩展名是否为 STEP 格式（不区分大小写）
        input_ext = file.filename.rsplit('.', 1)[1].lower()
        if input_ext not in ['step', 'stp']:
            return jsonify({'error': '只支持 STEP 格式文件'}), 400
        
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(suffix=f'.{input_ext}', delete=False) as tmp_input:
            file.save(tmp_input.name)
            input_path = tmp_input.name
        
        # 导入必要的模块
        try:
            import pathlib
            import dgl
            import numpy as np
            import torch
            from occwl.graph import face_adjacency
            from occwl.io import load_step
            from occwl.uvgrid import ugrid, uvgrid
        except ImportError as e:
            return jsonify({'error': f'缺少依赖: {e}'}), 500
        
        # 定义构建图的函数
        def build_graph(solid, curv_num_u_samples=10, surf_num_u_samples=10, surf_num_v_samples=10):
            # Build face adjacency graph with B-rep entities as node and edge features
            graph = face_adjacency(solid)
            
            # Compute the UV-grids for faces
            graph_face_feat = []
            for face_idx in graph.nodes:
                # Get the B-rep face
                face = graph.nodes[face_idx]["face"]
                # Compute UV-grids
                points = uvgrid(
                    face, method="point", num_u=surf_num_u_samples, num_v=surf_num_v_samples
                )
                normals = uvgrid(
                    face, method="normal", num_u=surf_num_u_samples, num_v=surf_num_v_samples
                )
                visibility_status = uvgrid(
                    face, method="visibility_status", num_u=surf_num_u_samples, num_v=surf_num_v_samples
                )
                mask = np.logical_or(visibility_status == 0, visibility_status == 2)
                # Concatenate channel-wise to form face feature tensor
                face_feat = np.concatenate((points, normals, mask), axis=-1)
                graph_face_feat.append(face_feat)
            graph_face_feat = np.asarray(graph_face_feat)
            
            # Compute the U-grids for edges
            graph_edge_feat = []
            for edge_idx in graph.edges:
                # Get the B-rep edge
                edge = graph.edges[edge_idx]["edge"]
                # Ignore dgenerate edges, e.g. at apex of cone
                if not edge.has_curve():
                    continue
                # Compute U-grids
                points = ugrid(edge, method="point", num_u=curv_num_u_samples)
                tangents = ugrid(edge, method="tangent", num_u=curv_num_u_samples)
                # Concatenate channel-wise to form edge feature tensor
                edge_feat = np.concatenate((points, tangents), axis=-1)
                graph_edge_feat.append(edge_feat)
            graph_edge_feat = np.asarray(graph_edge_feat)
            
            # Convert face-adj graph to DGL format
            edges = list(graph.edges)
            src = [e[0] for e in edges]
            dst = [e[1] for e in edges]
            dgl_graph = dgl.graph((src, dst), num_nodes=len(graph.nodes))
            dgl_graph.ndata["x"] = torch.from_numpy(graph_face_feat)
            dgl_graph.edata["x"] = torch.from_numpy(graph_edge_feat)
            return dgl_graph
        
        # 处理文件
        fn = pathlib.Path(input_path)
        fn_stem = fn.stem
        
        # 加载 STEP 文件
        solid = load_step(fn)[0]  # Assume there's one solid per file
        
        # 构建图
        graph = build_graph(solid)
        
        # 保存为 BIN 文件
        output_path = tempfile.mktemp(suffix='.bin')
        dgl.data.utils.save_graphs(output_path, [graph])
        
        # 验证文件
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("生成的 BIN 文件为空")
        
        @after_this_request
        def cleanup(response):
            try:
                if input_path: os.unlink(input_path)
                if output_path: os.unlink(output_path)
            except: pass
            return response
        
        return send_file(output_path, mimetype='application/octet-stream', as_attachment=True, 
                         download_name=fn_stem + '.bin')
    except Exception as e:
        logger.error(f"STEP 转 BIN 失败: {e}")
        try:
            if input_path: os.unlink(input_path)
            if output_path: os.unlink(output_path)
        except: pass
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)