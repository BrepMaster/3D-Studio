"""剖切功能 API 蓝图

使用 SectionService 处理剖切业务逻辑。
"""

import os
from flask import Blueprint, jsonify, request, send_file

from app.config import get_logger
from app.services import SectionService

section_bp = Blueprint('section', __name__, url_prefix='/api')
logger = get_logger()
section_service = SectionService()


@section_bp.route('/section-slice', methods=['POST'])
def get_section_slice():
    """获取剖切切片数据 API"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400

        data = request.json or {}
        sections = data.get('sections', [])

        result = section_service.process_section_slice(file, sections)
        return jsonify({'status': 'ok', **result})

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"获取剖切切片失败: {e}")
        return jsonify({'error': str(e)}), 500


@section_bp.route('/section-export', methods=['POST'])
def export_sectioned_model():
    """导出剖切后模型 API"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400

        data = request.json or {}

        output_path, output_suffix, mimetype = section_service.process_section_export(file, data)

        base_name = file.filename.rsplit('.', 1)[0]
        return send_file(
            output_path, mimetype=mimetype, as_attachment=True,
            download_name=base_name + '_section' + output_suffix
        )

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"导出剖切模型失败: {e}")
        return jsonify({'error': str(e)}), 500