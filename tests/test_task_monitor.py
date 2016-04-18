from datetime import datetime, timedelta
import signal
import subprocess
import time
import unittest

from . import tasks


class TestTaskMonitor(unittest.TestCase):
    def setUp(self):
        tasks.monitor.redis.flushdb()

    def test_state(self):
        # Schedule a task, check that we can inspect its state
        first_task = tasks.slow_echo.delay('first')
        queue = list(tasks.monitor.state())
        self.assertEqual(len(queue), 1)
        state = queue[0]
        self.assertEqual(state['id'], first_task.id)
        self.assertEqual(state['name'], 'slow_echo')
        self.assertEqual(state['state'], 'queued')
        self.assertAlmostEqual(state['queued'], datetime.now(),
                               delta=timedelta(seconds=5))

        # Schedule a second task
        second_task = tasks.slow_echo.delay('second')

        # Start the worker
        worker = self.start_worker()
        time.sleep(1)

        # Check that both tasks are in the queue and the first one is running
        queue = list(tasks.monitor.state())
        self.assertEqual([s['id'] for s in queue], [first_task.id, second_task.id])
        self.assertEqual([s['state'] for s in queue], ['running', 'queued'])

        # Tell the worker to execute the first task and wait for it to finish
        worker.send_signal(signal.SIGCONT)
        self.assertEqual(first_task.get(), 'first')

        # Check that the completed task is no longer in the queue
        queue = list(tasks.monitor.state())
        self.assertEqual(len(queue), 1)
        state = queue[0]
        self.assertEqual(state['id'], second_task.id)

        # Tell the worker to execute the second task and wait for it to finish
        worker.send_signal(signal.SIGCONT)
        self.assertEqual(second_task.get(), 'second')

        # Check that the queue is empty
        self.assertEqual(list(tasks.monitor.state()), [])

    def start_worker(self):
        command = 'celery worker -A tests.tasks -P solo -l INFO'.split()
        worker = subprocess.Popen(command,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.PIPE)
        self.addCleanup(worker.terminate)
        while b'ready' not in worker.stderr.readline():
            pass
        return worker
