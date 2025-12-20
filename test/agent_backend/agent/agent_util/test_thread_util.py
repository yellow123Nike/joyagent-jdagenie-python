import time
from agent_backend.agent.agent_util.thread_util import ThreadUtil, CountDownLatch

def test_execute_runs_task():
    result = []

    def task():
        result.append(1)

    ThreadUtil.execute(task)
    time.sleep(0.1)

    assert result == [1]

def test_count_down_latch():
    latch = CountDownLatch(2)
    result = []

    def task():
        result.append(1)
        latch.count_down()

    ThreadUtil.execute(task)
    ThreadUtil.execute(task)

    latch.await_()
    assert len(result) == 2
