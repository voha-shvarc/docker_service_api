import time
# from datetime import datetime
import datetime

import docker
from docker.errors import APIError
from .database import Task
import logging
# client = docker.from_env()
log = logging.getLogger(__name__)

TIMEOUT = datetime.timedelta(seconds=60)


class DockerClient:
    def __init__(self):
        self.client = docker.from_env()
        self.docker_status_to_task_status = {
            "created": Task.Status.pending,
            "running": Task.Status.running,
            "exited": Task.Status.finished
        }

    def run_container(self, image, command: [str, list]):
        if isinstance(command, list):
            command = f"/bin/sh -c \"{' && '.join(command)}\""

        log.info(f"{command = }")
        container = self.client.containers.run(
            image=image, command=command, detach=True
        )

        return container

    def kill_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.kill()

    def process_container(self, container, task_id):
        task = Task.get_by_id(task_id)
        task.status = self.docker_status_to_task_status[container.status]
        task.save()
        start = datetime.datetime.now()
        while container.status != "exited":
            time.sleep(1)
            running_time = datetime.datetime.now() - start
            log.info(f"{running_time = }")
            if running_time >= TIMEOUT:
                container.kill()
                logs = "Timeout Error. The process takes too long to proceed.\n" + str(container.logs())
                task.update(logs=logs, status=Task.Status.failed).execute()
                return

            container.reload()
            log.info(f"{container.status = }")
            if container.status != task.status:
                task.status = self.docker_status_to_task_status[container.status]

            task.logs = container.logs()
            task.save()
