from celery import signals
from redis import StrictRedis

__author__ = 'Omar Khan'
__email__ = 'omar@omarkhan.me'
__version__ = '0.0.1'


class TaskMonitor(object):
    """
    Uses celery signals to monitor tasks and store their status in redis.
    """
    def __init__(self, redis_url='redis://', redis_key='celery.monitor'):
        self.redis = StrictRedis.from_url(redis_url)
        self.redis_key = redis_key

    def state(self):
        """
        Return the current state of all pending tasks. Returns a mapping of
        task ids to their status ('queued' or 'running').
        """
        return {key.decode(): value.decode()
                for key, value in self.redis.hgetall(self.redis_key).items()}

    def monitor(self, task):
        """
        Decorate tasks with this to monitor their status.
        """
        signals.after_task_publish.connect(sender=task.name)(self._queued)
        signals.task_prerun.connect(sender=task)(self._running)
        signals.task_postrun.connect(sender=task)(self._complete)
        return task

    def _queued(self, sender, body, **kwargs):
        self.redis.hset(self.redis_key, body['id'], 'queued')

    def _running(self, sender, task_id, **kwargs):
        self.redis.hset(self.redis_key, task_id, 'running')

    def _complete(self, sender, task_id, **kwargs):
        self.redis.hdel(self.redis_key, task_id)
