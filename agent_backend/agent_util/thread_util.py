import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional


class CountDownLatch:
    def __init__(self, count: int):
        if count < 0:
            raise ValueError("count must be >= 0")
        self._count = count
        self._lock = threading.Lock()
        self._event = threading.Event()
        if self._count == 0:
            self._event.set()

    def count_down(self):
        with self._lock:
            if self._count <= 0:
                return
            self._count -= 1
            if self._count == 0:
                self._event.set()

    def await_(self):
        self._event.wait()


class ThreadUtil:
    _executor: Optional[ThreadPoolExecutor] = None
    _lock = threading.Lock()

    def __init__(self):
        raise RuntimeError("ThreadUtil cannot be instantiated")

    @classmethod
    def init_pool(cls, pool_size: int):
        with cls._lock:
            if cls._executor is None:
                max_pool_size = max(pool_size, 1000)
                cls._executor = ThreadPoolExecutor(
                    max_workers=max_pool_size,
                    thread_name_prefix="exe-pool",
                )

    @classmethod
    def execute(cls, runnable: Callable[[], None]):
        if cls._executor is None:
            cls.init_pool(100)
        cls._executor.submit(runnable)

    @staticmethod
    def get_count_down_latch(count: int) -> CountDownLatch:
        return CountDownLatch(count)

    @staticmethod
    def await_(latch: CountDownLatch):
        try:
            latch.await_()
        except Exception:
            pass

    @staticmethod
    def sleep(millis: int):
        try:
            time.sleep(millis / 1000.0)
        except Exception:
            pass
