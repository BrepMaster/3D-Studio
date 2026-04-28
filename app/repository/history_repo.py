"""历史记录数据访问模块

负责历史记录的持久化和访问操作。
"""

import os
import json
import uuid
import shutil
import zipfile
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

from app.config import get_logger, get_project_root

logger = get_logger()


class HistoryRepository:
    """历史记录数据访问类"""

    HISTORY_DIR = 'history'
    HISTORY_FILE = 'history.json'

    def __init__(self):
        self.project_root = get_project_root()
        self.history_dir = os.path.join(self.project_root, self.HISTORY_DIR)
        self.history_file_path = os.path.join(self.history_dir, self.HISTORY_FILE)
        self._ensure_history_dir()

    def _ensure_history_dir(self):
        """确保历史记录目录存在"""
        os.makedirs(self.history_dir, exist_ok=True)
        if not os.path.exists(self.history_file_path):
            with open(self.history_file_path, 'w') as f:
                json.dump([], f)

    def load_history(self) -> List[Dict]:
        """加载历史记录"""
        try:
            with open(self.history_file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error('历史记录文件格式错误')
            return []
        except OSError:
            logger.error('读取历史记录失败')
            return []

    def _save_history(self, history_list: List[Dict]):
        """保存历史记录"""
        with open(self.history_file_path, 'w') as f:
            json.dump(history_list, f, indent=2)

    def add_history(self, filename: str, file_path: str, file_size: int, file_format: str, thumbnail_path: Optional[str] = None) -> Optional[Dict]:
        """添加历史记录"""
        try:
            history_list = self.load_history()

            file_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()

            extension = os.path.splitext(filename)[1]
            stored_filename = f"{file_id}{extension}"
            stored_path = os.path.join(self.history_dir, stored_filename)

            shutil.copy(file_path, stored_path)

            thumbnail_name = None
            if thumbnail_path and os.path.exists(thumbnail_path):
                thumbnail_name = f"{file_id}_thumb.png"
                thumbnail_dest = os.path.join(self.history_dir, thumbnail_name)
                shutil.copy(thumbnail_path, thumbnail_dest)

            version = 1
            same_name_items = [item for item in history_list if item['filename'] == filename]
            if same_name_items:
                version = max(item.get('version', 1) for item in same_name_items) + 1

            history_item = {
                'id': file_id,
                'filename': filename,
                'format': file_format,
                'size': file_size,
                'path': stored_filename,
                'timestamp': timestamp,
                'thumbnail': thumbnail_name,
                'version': version
            }

            history_list.append(history_item)
            self._save_history(history_list)

            logger.info(f"添加历史记录: {filename}")
            return history_item
        except Exception as e:
            logger.error(f"添加历史记录失败: {e}")
            return None

    def remove_history(self, history_id: str) -> bool:
        """删除历史记录"""
        try:
            history_list = self.load_history()
            item_to_remove = None

            for item in history_list:
                if item['id'] == history_id:
                    item_to_remove = item
                    break

            if not item_to_remove:
                return False

            file_path = os.path.join(self.history_dir, item_to_remove['path'])
            if os.path.exists(file_path):
                os.remove(file_path)

            if item_to_remove.get('thumbnail'):
                thumbnail_path = os.path.join(self.history_dir, item_to_remove['thumbnail'])
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

            history_list = [item for item in history_list if item['id'] != history_id]
            self._save_history(history_list)

            logger.info(f"删除历史记录: {history_id}")
            return True
        except Exception as e:
            logger.error(f"删除历史记录失败: {e}")
            return False

    def clear_all(self):
        """清空所有历史记录"""
        try:
            history_list = self.load_history()
            for item in history_list:
                file_path = os.path.join(self.history_dir, item['path'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                if item.get('thumbnail'):
                    thumbnail_path = os.path.join(self.history_dir, item['thumbnail'])
                    if os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)

            self._save_history([])
            logger.info("清空所有历史记录")
        except Exception as e:
            logger.error(f"清空历史记录失败: {e}")

    def get_history_file_path(self, history_id: str) -> Optional[Tuple[str, Dict]]:
        """获取历史文件路径"""
        history_list = self.load_history()
        for item in history_list:
            if item['id'] == history_id:
                file_path = os.path.join(self.history_dir, item['path'])
                if os.path.exists(file_path):
                    return file_path, item
        return None, None

    def search_history(self, query: str = '', filters: Dict = None) -> List[Dict]:
        """搜索历史记录"""
        history_list = self.load_history()
        results = []

        for item in history_list:
            match = True

            if query and query.lower() not in item['filename'].lower():
                match = False

            if filters:
                if 'format' in filters and item['format'] != filters['format']:
                    match = False
                if 'min_size' in filters and item['size'] < filters['min_size']:
                    match = False
                if 'max_size' in filters and item['size'] > filters['max_size']:
                    match = False
                if 'date_from' in filters and item['timestamp'] < filters['date_from']:
                    match = False
                if 'date_to' in filters and item['timestamp'] > filters['date_to']:
                    match = False

            if match:
                results.append(item)

        return results

    def get_version_history(self, filename: str) -> List[Dict]:
        """获取文件的版本历史"""
        history_list = self.load_history()
        return sorted(
            [item for item in history_list if item['filename'] == filename],
            key=lambda x: x['version']
        )

    def get_specific_version(self, filename: str, version: int) -> Optional[Dict]:
        """获取文件的特定版本"""
        history_list = self.load_history()
        for item in history_list:
            if item['filename'] == filename and item.get('version') == version:
                return item
        return None

    def export_history(self, output_path: str, history_ids: List[str]) -> bool:
        """导出历史记录"""
        try:
            history_list = self.load_history()
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for history_id in history_ids:
                    for item in history_list:
                        if item['id'] == history_id:
                            file_path = os.path.join(self.history_dir, item['path'])
                            if os.path.exists(file_path):
                                zipf.write(file_path, os.path.basename(file_path))
                            break
            return True
        except Exception as e:
            logger.error(f"导出历史记录失败: {e}")
            return False

    def backup_history(self) -> Optional[str]:
        """备份历史记录"""
        try:
            backup_name = f"history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            backup_path = os.path.join(self.project_root, backup_name)

            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.history_file_path, 'history.json')

                for item in self.load_history():
                    file_path = os.path.join(self.history_dir, item['path'])
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
                    if item.get('thumbnail'):
                        thumbnail_path = os.path.join(self.history_dir, item['thumbnail'])
                        if os.path.exists(thumbnail_path):
                            zipf.write(thumbnail_path, os.path.basename(thumbnail_path))

            logger.info(f"备份历史记录: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"备份历史记录失败: {e}")
            return None

    def restore_history(self, backup_path: str) -> bool:
        """从备份恢复历史记录"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.project_root)

            logger.info(f"从备份恢复历史记录: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"恢复历史记录失败: {e}")
            return False