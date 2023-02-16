import enum
import peewee
from playhouse.pool import PooledSqliteDatabase

db = peewee.DatabaseProxy()
"""Deleted static/app.db from git"""


def init_database(testing=False):
    """Create required tables if they don't exist."""
    config = {
        'foreign_keys': 1,
    }
    if testing:
        db.initialize(PooledSqliteDatabase(':memory:', pragmas=config, check_same_thread=False))
        pass
    else:
        db.initialize(PooledSqliteDatabase("static/app.db", pragmas=config, check_same_thread=False))

    with db:
        db.create_tables([Task])


class Task(peewee.Model):
    class Meta:
        database = db

    class Status(str, enum.Enum):
        created = "created"
        pending = 'pending'
        running = 'running'
        finished = 'finished'
        failed = 'failed'

    title = peewee.CharField(max_length=20, null=False)
    """The name of the task."""
    image = peewee.CharField(max_length=255, null=False)
    """The image to run the command in."""
    command = peewee.CharField(max_length=255, null=False)
    """The command to run."""
    description = peewee.CharField(max_length=255, null=False)
    """The task that this result is for."""
    status = peewee.CharField(max_length=20, null=False, default=Status.pending.value)
    """The status of the task."""
    container_id = peewee.CharField(max_length=255, null=True)
    """The id of running container"""
    execution_time = peewee.IntegerField(null=True)
    """The execution time of the task."""
    logs = peewee.TextField(null=True)
    """The logs of the task."""
    def __str__(self):
        return f"Task {self.id}: {self.title}"

    def to_response(self, base_url: str) -> dict:
        return {
            "id": self.id,
            "type": "tasks",
            "attributes": {
                "title": self.title,
                "status": self.status,
                "image": self.image,
                "command": self.command,
                "description": self.description,
                "execution-time": self.execution_time
            },
            "links": {
                "self": f"{base_url}tasks/{self.id}",
                "logs": f"{base_url}tasks/{self.id}/logs"
            },

        }
