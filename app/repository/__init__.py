"""数据访问层（Repository）

负责数据持久化和访问操作，包括：
- 历史记录管理
- 文件存储
- 版本控制
"""

from .history_repo import HistoryRepository

__all__ = ['HistoryRepository']
