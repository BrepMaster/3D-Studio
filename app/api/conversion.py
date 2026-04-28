"""文件转换 API 蓝图

使用 ConversionService 处理转换业务逻辑。
"""

import os
from flask import Blueprint, send_file, jsonify, request, after_this_request

from app.config import get_logger
from app.services import ConversionService
from app.utils import format_file_size

conversion_bp = Blueprint('conversion', __name__, url_prefix='/api')
logger = get_logger()
conversion_service = ConversionService()


@conversion_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查 API"""
    return jsonify({'status': 'ok', 'message': 'PythonOCC Web服务运行中', 'version': '1.2.0'})


@conversion_bp.route('/sample', methods=['GET'])
def get_sample_model():
    """获取示例模型 API"""
    try:
        shape_type = request.args.get('type', 'box')
        output_path = conversion_service.get_sample_model(shape_type)
        return send_file(
            output_path,
            mimetype='application/sla',
            as_attachment=True,
            download_name=f'sample_{shape_type}.stl'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@conversion_bp.route('/upload', methods=['POST'])
def upload_and_convert():
    """文件上传和转换 API"""
    result_path = None
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        output_format = request.form.get('output_format', 'stl').lower()
        linear_deflection = float(request.form.get('linear_deflection', 0.1))
        angular_deflection = float(request.form.get('angular_deflection', 0.5))

        result_path, output_suffix, mimetype = conversion_service.upload_and_convert(
            file, output_format, linear_deflection, angular_deflection
        )

        original_filename = file.filename.rsplit('.', 1)[0] + output_suffix

        @after_this_request
        def cleanup(response):
            import gc
            try:
                if result_path and os.path.exists(result_path):
                    os.unlink(result_path)
                    logger.debug(f"Cleaned up temp file: {result_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")
            gc.collect()
            return response

        return send_file(
            result_path, mimetype=mimetype, as_attachment=True,
            download_name=original_filename
        )
    except ValueError as e:
        if result_path and os.path.exists(result_path):
            try:
                os.unlink(result_path)
            except Exception:
                pass
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        if result_path and os.path.exists(result_path):
            try:
                os.unlink(result_path)
            except Exception:
                pass
        logger.error(f"File conversion failed: {e}")
        return jsonify({'error': str(e)}), 500


@conversion_bp.route('/batch-upload', methods=['POST'])
def batch_upload():
    """批量文件上传和转换 API"""
    if 'files' not in request.files:
        return jsonify({'error': '未上传文件'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': '文件列表为空'}), 400

    output_format = request.form.get('output_format', 'stl').lower()
    linear_deflection = float(request.form.get('linear_deflection', 0.1))
    angular_deflection = float(request.form.get('angular_deflection', 0.5))

    try:
        zip_filename = conversion_service.batch_upload(
            files, output_format, linear_deflection, angular_deflection
        )

        return send_file(
            zip_filename, mimetype='application/zip',
            as_attachment=True, download_name='converted_files.zip'
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"批量转换失败: {e}")
        return jsonify({'error': str(e)}), 500