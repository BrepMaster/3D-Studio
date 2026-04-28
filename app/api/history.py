"""历史记录 API 蓝图

使用 HistoryService 处理历史记录业务逻辑。
"""

import os
import urllib.parse
from flask import Blueprint, send_file, jsonify, request

from app.config import get_logger, get_project_root, get_app
from app.services import HistoryService

history_bp = Blueprint('history', __name__, url_prefix='/api/history')
logger = get_logger()
history_service = HistoryService()


@history_bp.route('', methods=['GET'])
def get_history():
    """获取历史记录列表 API"""
    try:
        history_list = history_service.get_history()
        return jsonify({'status': 'ok', 'history': history_list})
    except Exception as e:
        logger.error(f'获取历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/<history_id>', methods=['GET'])
def get_history_item(history_id):
    """获取历史模型文件 API"""
    try:
        file_path = history_service.get_history_file_path(history_id)
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': '历史记录不存在'}), 404

        item = history_service.get_history_item(history_id)
        return send_file(file_path, as_attachment=False, download_name=item['filename'])
    except Exception as e:
        logger.error(f'获取历史文件失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/<history_id>', methods=['DELETE'])
def delete_history_item(history_id):
    """删除历史记录项 API"""
    try:
        if history_service.delete_history_item(history_id):
            return jsonify({'status': 'ok', 'message': '已删除历史记录'})
        else:
            return jsonify({'error': '历史记录不存在'}), 404
    except Exception as e:
        logger.error(f'删除历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/save', methods=['POST'])
def save_to_history():
    """保存上传的文件到历史记录 API"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400

        thumbnail_file = request.files.get('thumbnail')
        history_item = history_service.save_to_history(file, thumbnail_file)

        if history_item:
            return jsonify({
                'status': 'ok',
                'message': '已保存到历史记录',
                'historyItem': history_item
            })
        else:
            return jsonify({'error': '保存历史记录失败'}), 500
    except Exception as e:
        logger.error(f'保存到历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('', methods=['DELETE'])
def clear_history():
    """清空所有历史记录 API"""
    try:
        history_service.clear_history()
        return jsonify({'status': 'ok', 'message': '已清空历史记录'})
    except Exception as e:
        logger.error(f'清空历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/thumbnail/<history_id>', methods=['GET'])
def get_history_thumbnail(history_id):
    """获取历史记录缩略图 API"""
    try:
        thumbnail_path = history_service.get_history_thumbnail(history_id)
        if thumbnail_path:
            return send_file(thumbnail_path, mimetype='image/png')
        else:
            return jsonify({'error': '缩略图不存在'}), 404
    except Exception as e:
        logger.error(f'获取缩略图失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/search', methods=['GET'])
def search_history_items():
    """搜索和过滤历史记录 API"""
    try:
        query = request.args.get('query', '')
        format_filter = request.args.get('format', '')
        min_size = request.args.get('min_size', type=int)
        max_size = request.args.get('max_size', type=int)
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        filters = {}
        if format_filter:
            filters['format'] = format_filter
        if min_size is not None:
            filters['min_size'] = min_size
        if max_size is not None:
            filters['max_size'] = max_size
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to

        results = history_service.search_history(query, filters)
        return jsonify({'status': 'ok', 'history': results})
    except Exception as e:
        logger.error(f'搜索历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/versions/<filename>', methods=['GET'])
def get_file_versions(filename):
    """获取文件的版本历史 API"""
    try:
        decoded_filename = urllib.parse.unquote(filename)
        versions = history_service.get_version_history(decoded_filename)
        return jsonify({'status': 'ok', 'versions': versions})
    except Exception as e:
        logger.error(f'获取版本历史失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/version/<filename>/<int:version>', methods=['GET'])
def get_version(filename, version):
    """获取文件的特定版本 API"""
    try:
        decoded_filename = urllib.parse.unquote(filename)
        item = history_service.get_specific_version(decoded_filename, version)

        if not item:
            return jsonify({'error': '版本不存在'}), 404

        file_path = os.path.join(get_project_root(), 'history', item['path'])
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404

        return send_file(file_path, as_attachment=False, download_name=item['filename'])
    except Exception as e:
        logger.error(f'获取特定版本失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/export', methods=['POST'])
def export_history_items():
    """导出历史记录 API"""
    try:
        data = request.json or {}
        history_ids = data.get('history_ids', [])

        output_path = history_service.export_history(history_ids)
        if not output_path:
            return jsonify({'error': '导出失败'}), 500

        return send_file(
            output_path, mimetype='application/zip',
            as_attachment=True, download_name='history_export.zip'
        )
    except Exception as e:
        logger.error(f'导出历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/backup', methods=['GET'])
def backup_history_items():
    """备份历史记录 API"""
    try:
        backup_path = history_service.backup_history()
        if not backup_path:
            return jsonify({'error': '备份失败'}), 500

        return send_file(
            backup_path, mimetype='application/zip',
            as_attachment=True, download_name=os.path.basename(backup_path)
        )
    except Exception as e:
        logger.error(f'备份历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500


@history_bp.route('/restore', methods=['POST'])
def restore_history_items():
    """从备份恢复历史记录 API"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上传备份文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400

        success = history_service.restore_history(file)
        if success:
            return jsonify({'status': 'ok', 'message': '恢复成功'})
        else:
            return jsonify({'error': '恢复失败'}), 500
    except Exception as e:
        logger.error(f'恢复历史记录失败: {e}')
        return jsonify({'error': '服务器内部错误'}), 500