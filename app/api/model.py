"""模型分析 API 蓝图

使用 ModelService 处理模型分析业务逻辑。
"""

from flask import Blueprint, jsonify, request

from app.config import get_logger
from app.services import ModelService
from app.utils import create_error_response

model_bp = Blueprint('model', __name__, url_prefix='/api')
logger = get_logger()
model_service = ModelService()


@model_bp.route('/model-info', methods=['POST'])
def get_model_info():
    """获取模型拓扑信息 API"""
    if 'file' not in request.files:
        return create_error_response('未上传文件', 400)

    file = request.files['file']
    if file.filename == '':
        return create_error_response('文件名为空', 400)

    try:
        info = model_service.get_model_info(file)
        return jsonify(info)
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
        return create_error_response(str(e), 500)


@model_bp.route('/model-physical', methods=['POST'])
def get_model_physical_properties():
    """获取模型物理属性 API"""
    if 'file' not in request.files:
        return create_error_response('未上传文件', 400)

    file = request.files['file']
    if file.filename == '':
        return create_error_response('文件名为空', 400)

    try:
        props = model_service.get_model_physical_properties(file)
        return jsonify(props)
    except Exception as e:
        logger.error(f"获取模型物理属性失败: {e}")
        return create_error_response(str(e), 500)


@model_bp.route('/model-quality', methods=['POST'])
def get_model_quality_report():
    """获取模型质量评估报告 API"""
    if 'file' not in request.files:
        return create_error_response('未上传文件', 400)

    file = request.files['file']
    if file.filename == '':
        return create_error_response('文件名为空', 400)

    try:
        report = model_service.get_model_quality_report(file)
        return jsonify(report)
    except Exception as e:
        logger.error(f"获取模型质量报告失败: {e}")
        return create_error_response(str(e), 500)


@model_bp.route('/model-info-quick', methods=['POST'])
def api_get_model_info_quick():
    """快速获取模型基本信息 API"""
    if 'file' not in request.files:
        return create_error_response('未上传文件', 400)

    file = request.files['file']
    if file.filename == '':
        return create_error_response('文件名为空', 400)

    try:
        info = model_service.get_model_info_quick(file)
        return jsonify(info)
    except Exception as e:
        logger.error(f"快速获取模型信息失败: {e}")
        return create_error_response(str(e), 500)


@model_bp.route('/convert-settings', methods=['POST'])
def convert_settings():
    """保存转换设置 API（预留）"""
    try:
        data = request.json
        return jsonify({'status': 'ok', 'message': '设置已保存'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500