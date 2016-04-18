from datetime import datetime
from time import time

from celery import signals
from redis import StrictRedis

__author__ = 'Omar Khan'
__email__ = 'omar@omarkhan.me'
__version__ = '0.2.0'


class TaskMonitor(object):
    """
    Uses celery signals to monitor tasks and store their status in redis.
    """
    def __init__(self, redis_url='redis://',
                 redis_key_prefix='celery:monitor:'):
        self.redis = StrictRedis.from_url(redis_url)
        self.redis_state_key = redis_key_prefix + 'state'
        self.redis_order_key = redis_key_prefix + 'order'

    def state(self):
        """
        Yields the state of each task in the queue, in order.
        """
        with self.redis.pipeline() as redis:
            redis.hgetall(self.redis_state_key)
            redis.zrange(self.redis_order_key, 0, -1, withscores=True)
            state, order = redis.execute()
        for key, timestamp in order:
            task_name, task_id = self._split_task_key(key)
            yield {'id': task_id.decode(),
                   'name': task_name.decode(),
                   'queued': datetime.fromtimestamp(timestamp),
                   'state': state[task_id].decode()}

    def monitor(self, task):
        """
        Decorate tasks with this to monitor their status.
        """
        signals.after_task_publish.connect(sender=task.name)(self._queued)
        signals.task_prerun.connect(sender=task)(self._running)
        signals.task_postrun.connect(sender=task)(self._complete)
        return task

    def _queued(self, sender, body, **kwargs):
        with self.redis.pipeline() as redis:
            redis.hset(self.redis_state_key, body['id'], 'queued')
            redis.zadd(self.redis_order_key, time(),
                       self._task_key(sender, body['id']))
            redis.execute()

    def _running(self, sender, task_id, **kwargs):
        self.redis.hset(self.redis_state_key, task_id, 'running')

    def _complete(self, sender, task_id, **kwargs):
        with self.redis.pipeline() as redis:
            redis.hdel(self.redis_state_key, task_id)
            redis.zrem(self.redis_order_key,
                       self._task_key(sender.name, task_id))
            redis.execute()

    @staticmethod
    def _task_key(task_name, task_id):
        return '{0}:{1}'.format(task_name, task_id)

    @staticmethod
    def _split_task_key(key):
        return key.rsplit(b':', 1)
