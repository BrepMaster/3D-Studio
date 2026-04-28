"""历史记录模块测试"""

import os
import json
import sys
import pytest

os.environ['FLASK_ENV'] = 'testing'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.file_utils import format_file_size
from app.repository.history_repo import HistoryRepository


class TestFormatFileSize:
    """测试 format_file_size 函数"""

    def test_bytes(self):
        assert format_file_size(500) == '500.00 B'

    def test_kilobytes(self):
        assert format_file_size(1024) == '1.00 KB'

    def test_megabytes(self):
        assert format_file_size(1024 * 1024) == '1.00 MB'

    def test_gigabytes(self):
        assert format_file_size(1024 * 1024 * 1024) == '1.00 GB'


class TestSearchHistory:
    """测试 HistoryRepository.search_history 方法"""

    def test_empty_history(self, temp_history_dir):
        repo = HistoryRepository()
        repo.history_dir = temp_history_dir
        repo.history_file_path = os.path.join(temp_history_dir, 'history.json')
        with open(repo.history_file_path, 'w') as f:
            json.dump([], f)
        results = repo.search_history('test')
        assert results == []

    def test_search_by_filename(self, temp_history_dir):
        history_list = [
            {'id': '1', 'filename': 'test.step', 'format': 'step', 'size': 1000, 'timestamp': '', 'path': '1.step'},
            {'id': '2', 'filename': 'other.stl', 'format': 'stl', 'size': 2000, 'timestamp': '', 'path': '2.stl'}
        ]
        
        repo = HistoryRepository()
        repo.history_dir = temp_history_dir
        repo.history_file_path = os.path.join(temp_history_dir, 'history.json')
        with open(repo.history_file_path, 'w') as f:
            json.dump(history_list, f)
        
        results = repo.search_history('test')
        assert len(results) == 1
        assert results[0]['filename'] == 'test.step'

    def test_search_case_insensitive(self, temp_history_dir):
        history_list = [
            {'id': '1', 'filename': 'TEST.step', 'format': 'step', 'size': 1000, 'timestamp': '', 'path': '1.step'}
        ]
        
        repo = HistoryRepository()
        repo.history_dir = temp_history_dir
        repo.history_file_path = os.path.join(temp_history_dir, 'history.json')
        with open(repo.history_file_path, 'w') as f:
            json.dump(history_list, f)
        
        results = repo.search_history('test')
        assert len(results) == 1

    def test_filter_by_format(self, temp_history_dir):
        history_list = [
            {'id': '1', 'filename': 'test.step', 'format': 'step', 'size': 1000, 'timestamp': '', 'path': '1.step'},
            {'id': '2', 'filename': 'test.stl', 'format': 'stl', 'size': 2000, 'timestamp': '', 'path': '2.stl'}
        ]
        
        repo = HistoryRepository()
        repo.history_dir = temp_history_dir
        repo.history_file_path = os.path.join(temp_history_dir, 'history.json')
        with open(repo.history_file_path, 'w') as f:
            json.dump(history_list, f)
        
        results = repo.search_history('', filters={'format': 'stl'})
        assert len(results) == 1
        assert results[0]['format'] == 'stl'

    def test_filter_by_size_range(self, temp_history_dir):
        history_list = [
            {'id': '1', 'filename': 'small.step', 'format': 'step', 'size': 500, 'timestamp': '', 'path': '1.step'},
            {'id': '2', 'filename': 'large.step', 'format': 'step', 'size': 5000, 'timestamp': '', 'path': '2.step'}
        ]
        
        repo = HistoryRepository()
        repo.history_dir = temp_history_dir
        repo.history_file_path = os.path.join(temp_history_dir, 'history.json')
        with open(repo.history_file_path, 'w') as f:
            json.dump(history_list, f)
        
        results = repo.search_history('', filters={'min_size': 1000, 'max_size': 10000})
        assert len(results) == 1
        assert results[0]['filename'] == 'large.step'
