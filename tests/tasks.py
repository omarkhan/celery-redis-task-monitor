import signal
import time

from celery import Celery

from task_monitor import TaskMonitor


app = Celery('tasks', broker='redis://', backend='redis://')
monitor = TaskMonitor()


light = 'red'


def handler(*args, **kwargs):
    global light
    light = 'green'
signal.signal(signal.SIGCONT, handler)


@monitor.monitor
@app.task(name='slow_echo')
def slow_echo(message):
    """
    Waits for the worker to receive the SIGCONT signal, then echoes the input.
    """
    global light
    while light != 'green':
        time.sleep(0.5)
    light = 'red'
    return message
