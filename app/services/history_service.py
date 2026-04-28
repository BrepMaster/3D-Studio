"""历史记录服务模块

负责处理历史记录的业务逻辑。
"""

import os
import json
import tempfile
from typing import List, Dict, Optional

from app.config import get_logger, get_project_root
from app.repository import HistoryRepository
from app.utils import format_file_size
from app.temp_file_manager import temp_file

logger = get_logger()


class HistoryService:
    """历史记录服务"""

    def __init__(self):
        self.repo = HistoryRepository()

    def format_history_item(self, item: Dict) -> Dict:
        """格式化历史记录项"""
        return {
            'id': item['id'],
            'filename': item['filename'],
            'format': item['format'],
            'size': item['size'],
            'sizeFormatted': format_file_size(item['size']),
            'timestamp': item['timestamp'],
            'thumbnail': item.get('thumbnail'),
            'version': item.get('version', 1)
        }

    def get_history(self) -> List[Dict]:
        """获取历史记录列表"""
        history_list = self.repo.load_history()
        return [self.format_history_item(item) for item in history_list]

    def get_history_item(self, history_id: str) -> Optional[Dict]:
        """获取历史记录项"""
        file_path, item = self.repo.get_history_file_path(history_id)
        if file_path and item:
            return item
        return None

    def get_history_file_path(self, history_id: str) -> Optional[str]:
        """获取历史文件路径"""
        file_path, _ = self.repo.get_history_file_path(history_id)
        return file_path

    def delete_history_item(self, history_id: str) -> bool:
        """删除历史记录项"""
        return self.repo.remove_history(history_id)

    def save_to_history(self, file, thumbnail_file=None) -> Optional[Dict]:
        """保存文件到历史记录"""
        with temp_file(suffix=os.path.splitext(file.filename)[1]) as temp_path:
            file.save(temp_path)
            file_size = os.path.getsize(temp_path)

            thumbnail_path = None
            if thumbnail_file and thumbnail_file.filename:
                thumbnail_path = tempfile.mktemp(suffix='.png')
                thumbnail_file.save(thumbnail_path)

            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'stl'

            result = self.repo.add_history(
                file.filename, temp_path, file_size, ext, thumbnail_path
            )

            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    os.unlink(thumbnail_path)
                except Exception:
                    pass

            return result

    def clear_history(self):
        """清空所有历史记录"""
        self.repo.clear_all()

    def get_history_thumbnail(self, history_id: str) -> Optional[str]:
        """获取历史记录缩略图"""
        history_list = self.repo.load_history()
        for item in history_list:
            if item['id'] == history_id and 'thumbnail' in item and item['thumbnail']:
                thumbnail_path = os.path.join(get_project_root(), 'history', item['thumbnail'])
                if os.path.exists(thumbnail_path):
                    return thumbnail_path
        return None

    def search_history(self, query: str = '', filters: Dict = None) -> List[Dict]:
        """搜索历史记录"""
        results = self.repo.search_history(query, filters)
        return [self.format_history_item(item) for item in results]

    def get_version_history(self, filename: str) -> List[Dict]:
        """获取文件的版本历史"""
        versions = self.repo.get_version_history(filename)
        return [self.format_history_item(item) for item in versions]

    def get_specific_version(self, filename: str, version: int) -> Optional[Dict]:
        """获取文件的特定版本"""
        return self.repo.get_specific_version(filename, version)

    def export_history(self, history_ids: List[str]) -> Optional[str]:
        """导出历史记录"""
        with temp_file(suffix='.zip') as output_path:
            if self.repo.export_history(output_path, history_ids):
                return output_path
        return None

    def backup_history(self) -> Optional[str]:
        """备份历史记录"""
        return self.repo.backup_history()

    def restore_history(self, backup_file) -> bool:
        """从备份恢复历史记录"""
        with temp_file(suffix='.zip') as backup_path:
            backup_file.save(backup_path)
            return self.repo.restore_history(backup_path)