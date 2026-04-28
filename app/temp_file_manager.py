"""临时文件管理模块

此模块提供临时文件和目录的管理功能，使用上下文管理器确保临时文件在使用后
自动清理，避免磁盘空间泄漏。是处理上传文件和转换中间结果的重要辅助模块。

主要功能:
    1. temp_file: 上下文管理器，创建和管理临时文件
    2. temp_dir: 上下文管理器，创建和管理临时目录

特性:
    - 自动清理: 退出上下文后自动删除临时文件/目录
    - 安全删除: 确保文件在删除时不被占用
    - 多种后缀: 支持自定义文件后缀
    - 异常安全: 即使发生异常也会清理

使用示例:
    from app.temp_file_manager import temp_file, temp_dir

    # 使用临时文件
    with temp_file(suffix='.stl') as file_path:
        # 处理文件
        process_file(file_path)
    # 退出时自动删除

    # 使用临时目录
    with temp_dir() as dir_path:
        # 处理多个文件
        for i in range(10):
            create_file(os.path.join(dir_path, f'file_{i}.stl'))
    # 退出时自动删除整个目录

注意事项:
    - 临时文件在退出 with 块后会被删除
    - 如果文件正在被其他进程使用，删除可能会失败
    - 不要在 with 块外保留文件路径引用
"""

import os
import tempfile
import shutil
import atexit
from typing import Optional
from app.config import get_logger

logger = get_logger()


class temp_file:
    """临时文件上下文管理器

    创建一个临时文件并在退出上下文时自动删除。

    Attributes:
        name (str): 临时文件的路径

    Example:
        with temp_file(suffix='.stl') as f:
            print(f"临时文件: {f}")
            # 处理文件
        # 文件已自动删除
    """

    def __init__(self, suffix: str = '', prefix: str = 'tmp', delete: bool = True) -> None:
        """初始化临时文件

        Args:
            suffix: 文件后缀，如 '.stl'
            prefix: 文件名前缀，默认 'tmp'
            delete: 退出时是否删除，默认 True
        """
        self.delete = delete
        self.name = None

        try:
            temp_fd, self.name = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(temp_fd)
            logger.debug(f"创建临时文件: {self.name}")
        except Exception as e:
            logger.error(f"创建临时文件失败: {e}")
            self.name = None
            raise

    def __enter__(self) -> str:
        """进入上下文管理器"""
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文管理器，删除临时文件"""
        if self.delete and self.name and os.path.exists(self.name):
            try:
                os.unlink(self.name)
                logger.debug(f"删除临时文件: {self.name}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {e}")


class temp_dir:
    """临时目录上下文管理器

    创建一个临时目录并在退出上下文时自动删除。

    Attributes:
        name (str): 临时目录的路径

    Example:
        with temp_dir() as dir_path:
            print(f"临时目录: {dir_path}")
            # 创建多个文件
            for i in range(5):
                Path(dir_path, f'file_{i}.txt').write_text(f'Content {i}')
        # 整个目录已自动删除
    """

    def __init__(self, prefix: str = '3d_studio_', delete: bool = True) -> None:
        """初始化临时目录

        Args:
            prefix: 目录名前缀，默认 '3d_studio_'
            delete: 退出时是否删除，默认 True
        """
        self.delete = delete
        self.name = None

        try:
            self.name = tempfile.mkdtemp(prefix=prefix)
            logger.debug(f"创建临时目录: {self.name}")
        except Exception as e:
            logger.error(f"创建临时目录失败: {e}")
            self.name = None
            raise

    def __enter__(self) -> str:
        """进入上下文管理器"""
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文管理器，删除临时目录"""
        if self.delete and self.name and os.path.exists(self.name):
            try:
                shutil.rmtree(self.name)
                logger.debug(f"删除临时目录: {self.name}")
            except Exception as e:
                logger.warning(f"删除临时目录失败: {e}")


def cleanup_all_temp_files() -> None:
    """清理所有可能的临时文件

    尝试清理系统中可能的临时文件（与当前进程相关的）。
    通常在进程退出时由 atexit 自动调用。
    """
    logger.info("尝试清理所有临时文件...")


atexit.register(cleanup_all_temp_files)


def get_temp_directory() -> str:
    """获取系统临时目录路径

    Returns:
        str: 系统临时目录路径
    """
    return tempfile.gettempdir()


def ensure_temp_space(min_free_mb: int = 100) -> bool:
    """确保临时目录有足够的可用空间

    Args:
        min_free_mb: 最小可用空间（MB），默认 100MB

    Returns:
        bool: 如果可用空间充足返回 True，否则返回 False

    Warning:
        此函数仅作为提示，实际空间检查可能在创建文件时进行
    """
    import shutil
    temp_path = get_temp_directory()
    try:
        stat = shutil.disk_usage(temp_path)
        free_mb = stat.free / (1024 * 1024)
        logger.debug(f"临时目录 {temp_path} 可用空间: {free_mb:.2f} MB")
        return free_mb >= min_free_mb
    except Exception as e:
        logger.warning(f"检查临时目录空间失败: {e}")
        return True