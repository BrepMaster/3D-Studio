"""文件转换服务模块

负责处理文件转换的业务逻辑。
"""

import os
import tempfile
import zipfile
from typing import Tuple, Optional, List

from app.config import get_logger, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.core import (
    read_file_by_extension,
    shape_to_stl,
    shape_to_obj,
    shape_to_gltf,
    shape_to_step,
    shape_to_iges,
    get_output_format_info
)
from app.utils import format_file_size, create_sample_shape
from app.temp_file_manager import temp_file, temp_dir

logger = get_logger()


class ConversionService:
    """文件转换服务"""

    OUTPUT_FORMAT_CONFIG = {
        'stl': {
            'suffix': '.stl',
            'mimetype': 'application/sla',
            'converter': shape_to_stl,
            'requires_deflection': True
        },
        'obj': {
            'suffix': '.obj',
            'mimetype': 'text/plain',
            'converter': shape_to_obj,
            'requires_deflection': True
        },
        'step': {
            'suffix': '.step',
            'mimetype': 'application/step',
            'converter': shape_to_step,
            'requires_deflection': False,
            'check_empty': True
        },
        'gltf': {
            'suffix': '.gltf',
            'mimetype': 'model/gltf+json',
            'converter': shape_to_gltf,
            'requires_deflection': True
        },
        'igs': {
            'suffix': '.igs',
            'mimetype': 'application/iges',
            'converter': shape_to_iges,
            'requires_deflection': False
        },
        'bin': {
            'suffix': '.bin',
            'mimetype': 'application/octet-stream',
            'converter': None,
            'requires_deflection': False,
            'check_empty': True
        }
    }

    def __init__(self):
        pass

    def validate_file(self, file) -> Tuple[bool, Optional[str], Optional[int]]:
        """验证上传的文件"""
        if not file or file.filename == '':
            return False, '文件名为空', 400

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return False, '文件大小超过限制（100MB）', 400

        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return False, '不支持的文件类型', 400

        return True, ext, file_size

    def convert_shape(self, shape, output_format: str, linear_deflection: float, angular_deflection: float, input_path: str = None) -> Tuple[str, str, str]:
        """转换几何形状为指定格式"""
        config = self.OUTPUT_FORMAT_CONFIG.get(output_format) or self.OUTPUT_FORMAT_CONFIG['stl']
        output_suffix = config['suffix']
        mimetype = config['mimetype']
        converter = config['converter']

        temp = tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False)
        output_path = temp.name
        temp.close()

        try:
            if output_format == 'bin':
                if not input_path:
                    raise ValueError("BIN 格式转换需要输入文件路径")
                try:
                    import pathlib
                    import dgl
                    from occwl.io import load_step
                    from app.utils import build_graph
                except ImportError as e:
                    raise Exception(f"缺少 BIN 格式依赖: {e}")
                
                fn = pathlib.Path(input_path)
                solid = load_step(fn)[0]
                graph = build_graph(solid)
                if not graph:
                    raise Exception("构建图失败")
                
                if not isinstance(graph, dgl.DGLGraph):
                    try:
                        import networkx as nx
                        if isinstance(graph, nx.Graph):
                            graph = dgl.from_networkx(graph)
                        else:
                            raise Exception(f"不支持的图类型: {type(graph)}")
                    except Exception as e:
                        raise Exception(f"图类型转换失败: {e}")
                
                dgl.data.utils.save_graphs(output_path, [graph])
                result_path = output_path
            elif config['requires_deflection']:
                result_path = converter(shape, output_path, linear_deflection, angular_deflection)
            else:
                result_path = converter(shape, output_path)

            if result_path.endswith('.stl'):
                mimetype = 'application/sla'
                output_suffix = '.stl'
                if output_format != 'stl':
                    logger.info(f"{output_format.upper()} export failed, falling back to STL")

            if config.get('check_empty'):
                if not os.path.exists(result_path) or os.path.getsize(result_path) == 0:
                    raise Exception("Generated file is empty")
                logger.info(f"Final output file: {result_path}, size: {os.path.getsize(result_path)} bytes")

            return result_path, output_suffix, mimetype
        except Exception:
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file: {e}")
            raise

    def process_file_conversion(self, input_path: str, input_ext: str, output_format: str, linear_deflection: float, angular_deflection: float) -> Tuple[str, str, str]:
        """处理文件转换"""
        import gc
        shape = None
        try:
            shape = read_file_by_extension(input_path, input_ext)
            result = self.convert_shape(shape, output_format, linear_deflection, angular_deflection, input_path)
            return result
        finally:
            del shape
            gc.collect()

    def upload_and_convert(self, file, output_format: str = 'stl', linear_deflection: float = 0.1, angular_deflection: float = 0.5) -> Tuple[str, str, str]:
        """上传文件并转换"""
        success, ext_or_error, file_size_or_code = self.validate_file(file)
        
        if not success:
            raise ValueError(f"{ext_or_error}")

        ext = ext_or_error
        file_size = file_size_or_code

        logger.info(f'Starting file conversion: {file.filename} ({format_file_size(file_size)}) -> {output_format}')

        result_path = None
        try:
            with temp_file(suffix=f'.{ext}') as input_path:
                file.save(input_path)
                result_path, output_suffix, mimetype = self.process_file_conversion(
                    input_path, ext, output_format,
                    linear_deflection, angular_deflection
                )
                return result_path, output_suffix, mimetype
        except Exception:
            if result_path and os.path.exists(result_path):
                try:
                    os.unlink(result_path)
                except Exception:
                    pass
            raise

    def get_sample_model(self, shape_type: str = 'box') -> str:
        """获取示例模型"""
        shape = create_sample_shape(shape_type)
        with temp_file(suffix='.stl') as output_path:
            shape_to_stl(shape, output_path)
            return output_path

    def convert_shape_to_file(self, shape, base_name: str, temp_dir_path: str, output_format: str, linear_deflection: float, angular_deflection: float, filename: str, input_path: str) -> Optional[str]:
        """转换单个文件"""
        if output_format == 'bin':
            try:
                import pathlib
                import dgl
                from occwl.io import load_step
                from app.utils import build_graph
            except ImportError as e:
                logger.error(f"缺少依赖: {e}")
                return None

            fn = pathlib.Path(input_path)
            solid = load_step(fn)[0]
            graph = build_graph(solid)
            if not graph:
                logger.error(f"构建图失败: {filename}")
                return None

            output_filename = os.path.join(temp_dir_path, base_name + '.bin')
            dgl.data.utils.save_graphs(output_filename, [graph])

            if not os.path.exists(output_filename) or os.path.getsize(output_filename) == 0:
                logger.error(f"生成的 BIN 文件为空: {output_filename}")
                return None

            logger.info(f"成功转换文件: {filename} -> {os.path.basename(output_filename)}")
            return output_filename

        config = self.OUTPUT_FORMAT_CONFIG.get(output_format) or self.OUTPUT_FORMAT_CONFIG['stl']
        output_suffix = config['suffix']
        converter = config['converter']

        output_filename = os.path.join(temp_dir_path, base_name + output_suffix)

        try:
            if config['requires_deflection']:
                result = converter(shape, output_filename, linear_deflection, angular_deflection)
            else:
                result = converter(shape, output_filename)

            if result.endswith('.stl') and output_format != 'stl':
                logger.info(f"{output_format.upper()} 导出失败，已回退到 STL 格式: {filename}")

            if config.get('check_empty'):
                if not os.path.exists(result) or os.path.getsize(result) == 0:
                    logger.error(f"生成的文件为空: {result}")
                    return None
                if result.endswith('.step'):
                    try:
                        with open(result, 'r') as f:
                            content = f.read()
                        if 'ISO-10303-21' not in content:
                            logger.error(f"生成的 STEP 文件不包含有效的 STEP 数据: {result}")
                            return None
                    except Exception as e:
                        logger.error(f"检查 STEP 文件内容失败: {e}")
                        return None

            logger.info(f"成功转换文件: {filename} -> {os.path.basename(result)}")
            return result
        except Exception as e:
            logger.error(f"转换文件 {filename} 失败: {e}")
            return None

    def process_batch_conversion(self, files: List, output_format: str, linear_deflection: float, angular_deflection: float) -> List[str]:
        """处理批量文件转换"""
        converted_files = []

        with temp_dir() as temp_dir_path:
            for file in files:
                if file.filename == '':
                    continue

                input_ext = file.filename.rsplit('.', 1)[1].lower()
                if input_ext not in ALLOWED_EXTENSIONS:
                    continue

                if output_format == 'bin' and input_ext not in ['step', 'stp']:
                    logger.warning(f"BIN 格式只支持 STEP 文件: {file.filename}")
                    continue

                with temp_file(suffix=f'.{input_ext}') as input_path:
                    file.save(input_path)

                    try:
                        shape = read_file_by_extension(input_path, input_ext)
                        base_name = file.filename.rsplit('.', 1)[0]

                        result = self.convert_shape_to_file(
                            shape, base_name, temp_dir_path,
                            output_format, linear_deflection, angular_deflection,
                            file.filename, input_path
                        )

                        if result:
                            converted_files.append(result)
                    except Exception as e:
                        logger.error(f"处理文件 {file.filename} 失败: {e}")
                        continue

        return converted_files

    def batch_upload(self, files: List, output_format: str = 'stl', linear_deflection: float = 0.1, angular_deflection: float = 0.5) -> str:
        """批量上传并转换文件"""
        logger.info(f'Starting batch conversion, {len(files)} files -> {output_format}')

        converted_files = self.process_batch_conversion(
            files, output_format, linear_deflection, angular_deflection
        )
        
        if not converted_files:
            raise ValueError('没有可转换的文件')

        logger.info(f'批量转换完成，成功转换 {len(converted_files)} 个文件')

        with temp_file(suffix='.zip') as zip_filename:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for cf in converted_files:
                    zipf.write(cf, os.path.basename(cf))
            logger.info(f'生成 ZIP 包，包含 {len(converted_files)} 个转换文件')
            return zip_filename