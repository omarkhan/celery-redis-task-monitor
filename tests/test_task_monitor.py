import signal
import subprocess
import time
import unittest

from . import tasks


class TestTaskMonitor(unittest.TestCase):
    def setUp(self):
        tasks.monitor.redis.flushdb()

    def test_state(self):
        task = tasks.slow_echo.delay('test')
        self.assertEqual(tasks.monitor.state(), {task.id: 'queued'})
        worker = self.start_worker()
        time.sleep(1)
        self.assertEqual(tasks.monitor.state(), {task.id: 'running'})
        worker.send_signal(signal.SIGCONT)
        self.assertEqual(task.get(), 'test')
        self.assertEqual(tasks.monitor.state(), {})

    def start_worker(self):
        worker = subprocess.Popen('celery worker -A tests.tasks -P solo -l INFO'.split(),
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        self.addCleanup(worker.terminate)
        while b'ready' not in worker.stderr.readline():
            pass
        return worker
