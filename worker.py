import threading
import queue
import time
import json

from app.database import Task, init_database
from app.docker_client import DockerClient
from docker.errors import APIError
import typing

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


LOG = logging.getLogger(__name__)


class Worker:
    def __init__(self, num_of_workers=1):
        self.queue = queue.Queue()
        self.num_of_workers = num_of_workers
        self.docker_client = DockerClient()

    def start_workers(self):
        LOG.info("Starting %s workers.", self.num_of_workers)
        for i in range(self.num_of_workers):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            item = self.queue.get()
            self._process_task(item)
            self.queue.task_done()

    def wait(self):
        """Wait for all tasks to be processed."""
        self.queue.join()

    def _put_task(self, task: Task):
        self.queue.put(task)

    def _process_task(self, task: Task):
        LOG.info("Processing task %s.", task)

        image = task.image
        command = json.loads(task.command)

        try:
            container = self.docker_client.run_container(image, command)
        except APIError as e:
            LOG.info("Api error" + e.explanation)
            task.status = Task.Status.failed
            task.logs = e.explanation
            task.save()
        else:
            task.update(container_id=container.id).execute()
            self.docker_client.process_container(container, task.id)

    def _gather_tasks(self) -> typing.Sequence[Task]:
        """Gather all tasks.py in the database."""
        tasks = Task.select().where(Task.status == "pending")
        return tasks

    def start(self):
        init_database()
        self.start_workers()

        while True:
            tasks = self._gather_tasks()
            if tasks:
                LOG.info("PUtting tasks")
                for task in tasks:
                    self._put_task(task)
            else:
                LOG.info("No tasks found, sleeping for 1 seconds.")
                time.sleep(1)

            self.wait()


w = Worker(num_of_workers=2)
w.start()
