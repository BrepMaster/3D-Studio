"""异步任务管理模块

提供异步任务执行和管理功能。
"""

import concurrent.futures
import threading
import time
from typing import Callable, Any, Tuple, Optional


class AsyncTaskManager:
    """异步任务管理器"""

    _instance = None
    _thread_pool = None
    _lock = threading.Lock()
    _task_count = 0
    _max_pending_tasks = 5
    _max_workers = 2

    def __new__(cls, max_workers: int = 2):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._thread_pool = concurrent.futures.ThreadPoolExecutor(
                    max_workers=cls._max_workers,
                    thread_name_prefix='3d-studio-worker'
                )
                print(f"[TaskManager] Created thread pool with {cls._max_workers} workers")
            return cls._instance

    def submit(self, task_func: Callable, *args) -> concurrent.futures.Future:
        """提交任务到线程池"""
        with self._lock:
            if self._task_count >= self._max_pending_tasks:
                print(f"[TaskManager] Task queue full ({self._task_count}/{self._max_pending_tasks}), rejecting")
                raise Exception("系统繁忙，请稍后重试")
            self._task_count += 1
            print(f"[TaskManager] Submitted task, current count: {self._task_count}")

        def wrapped_task(*task_args):
            start_time = time.time()
            thread_id = threading.current_thread().ident
            print(f"[TaskManager] Thread {thread_id} starting task")
            try:
                result = task_func(*task_args)
                elapsed = time.time() - start_time
                print(f"[TaskManager] Thread {thread_id} completed task in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"[TaskManager] Thread {thread_id} task failed in {elapsed:.2f}s: {e}")
                raise
            finally:
                with self._lock:
                    self._task_count -= 1
                    print(f"[TaskManager] Task completed, current count: {self._task_count}")

        return self._thread_pool.submit(wrapped_task, *args)

    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        with self._lock:
            if self._thread_pool:
                print("[TaskManager] Shutting down thread pool")
                self._thread_pool.shutdown(wait=wait)
                self._thread_pool = None


def handle_async_task(
    task_func: Callable,
    *args,
    timeout: int = 90
) -> Tuple[Any, Optional[str], Optional[int]]:
    """处理异步任务"""
    task_manager = AsyncTaskManager()
    try:
        print(f"[AsyncTask] Submitting task with timeout {timeout}s")
        future = task_manager.submit(task_func, *args)
        result = future.result(timeout=timeout)
        print("[AsyncTask] Task completed successfully")
        return result, None, None
    except concurrent.futures.TimeoutError:
        print("[AsyncTask] Task timed out")
        return None, '操作超时，请尝试使用较小的模型文件', 500
    except Exception as e:
        print(f"[AsyncTask] Task failed: {e}")
        from app.config import get_logger
        logger = get_logger()
        logger.error(f"异步任务失败: {e}")
        return None, str(e), 500