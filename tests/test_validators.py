"""验证器模块测试"""

import os
import sys
import pytest

os.environ['FLASK_ENV'] = 'testing'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.validators import (
    validate_file_extension,
    validate_output_format,
    validate_deflection_params,
    validate_section_config,
    validate_bbox,
    validate_history_id,
    validate_search_params
)


class TestValidateFileExtension:
    """测试 validate_file_extension 函数"""

    def test_valid_extension(self):
        assert validate_file_extension('model.step') == (True, 'step')
        assert validate_file_extension('model.STEP') == (True, 'step')
        assert validate_file_extension('model.stl') == (True, 'stl')
        assert validate_file_extension('model.iges') == (True, 'iges')

    def test_invalid_extension(self):
        valid, result = validate_file_extension('model.txt')
        assert valid is False
        assert '不支持' in result

    def test_no_extension(self):
        valid, result = validate_file_extension('noextension')
        assert valid is False
        assert '缺少扩展名' in result

    def test_empty_filename(self):
        valid, result = validate_file_extension('')
        assert valid is False


class TestValidateOutputFormat:
    """测试 validate_output_format 函数"""

    def test_valid_formats(self):
        assert validate_output_format('stl') == (True, None)
        assert validate_output_format('obj') == (True, None)
        assert validate_output_format('STEP') == (True, None)
        assert validate_output_format('gltf') == (True, None)

    def test_invalid_format(self):
        valid, error = validate_output_format('pdf')
        assert valid is False
        assert '不支持' in error

    def test_empty_format(self):
        valid, error = validate_output_format('')
        assert valid is False


class TestValidateDeflectionParams:
    """测试 validate_deflection_params 函数"""

    def test_valid_params(self):
        valid, linear, angular, error = validate_deflection_params(0.1, 0.5)
        assert valid is True
        assert linear == 0.1
        assert angular == 0.5
        assert error is None

    def test_default_params(self):
        valid, linear, angular, error = validate_deflection_params(None, None)
        assert valid is True
        assert linear == 0.1
        assert angular == 0.5

    def test_invalid_linear(self):
        valid, _, _, error = validate_deflection_params('invalid', 0.5)
        assert valid is False
        assert '线性偏差' in error

    def test_linear_out_of_range(self):
        valid, _, _, error = validate_deflection_params(10.0, 0.5)
        assert valid is False
        assert '0.001' in error


class TestValidateSectionConfig:
    """测试 validate_section_config 函数"""

    def test_valid_config(self):
        valid, error = validate_section_config({
            'axis': 'z',
            'offset': 50,
            'enabled': True
        })
        assert valid is True
        assert error is None

    def test_invalid_axis(self):
        valid, error = validate_section_config({
            'axis': 'w',
            'offset': 0
        })
        assert valid is False
        assert '无效的轴' in error

    def test_offset_out_of_range(self):
        valid, error = validate_section_config({
            'axis': 'z',
            'offset': 200
        })
        assert valid is False
        assert '偏移值' in error

    def test_invalid_config_type(self):
        valid, error = validate_section_config("not a dict")
        assert valid is False


class TestValidateBBox:
    """测试 validate_bbox 函数"""

    def test_valid_bbox(self):
        valid, error = validate_bbox({
            'min': [0, 0, 0],
            'max': [10, 10, 10],
            'size': [10, 10, 10]
        })
        assert valid is True
        assert error is None

    def test_invalid_bbox_type(self):
        valid, error = validate_bbox("not a dict")
        assert valid is False

    def test_missing_keys(self):
        valid, error = validate_bbox({'min': [0, 0, 0]})
        assert valid is False
        assert '缺少必需的键' in error

    def test_invalid_bbox_values(self):
        valid, error = validate_bbox({
            'min': [0, 0],
            'max': [10, 10, 10],
            'size': [10, 10, 10]
        })
        assert valid is False


class TestValidateHistoryId:
    """测试 validate_history_id 函数"""

    def test_valid_uuid(self):
        assert validate_history_id('123e4567-e89b-12d3-a456-426614174000') == (True, None)

    def test_invalid_uuid(self):
        valid, error = validate_history_id('not-a-uuid')
        assert valid is False
        assert '无效的历史记录ID' in error

    def test_empty_id(self):
        valid, error = validate_history_id('')
        assert valid is False


class TestValidateSearchParams:
    """测试 validate_search_params 函数"""

    def test_valid_params(self):
        valid, error = validate_search_params({
            'min_size': 100,
            'max_size': 1000
        })
        assert valid is True

    def test_invalid_min_size(self):
        valid, error = validate_search_params({'min_size': -1})
        assert valid is False

    def test_min_greater_than_max(self):
        valid, error = validate_search_params({
            'min_size': 1000,
            'max_size': 100
        })
        assert valid is False
        assert '不能大于' in error
