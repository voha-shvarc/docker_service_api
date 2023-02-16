import flask

import logging
import json
import sys

from .database import Task
from .utils import is_tasks_amount_under_limit
from .docker_client import DockerClient


blueprint = flask.Blueprint("tasks", __name__)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
LOG = logging.getLogger(__name__)


@blueprint.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.select()
    is_tasks_amount_under_limit()
    return flask.jsonify({
        "data": [task.to_response(flask.request.base_url) for task in tasks],
        "links": f"{flask.request.base_url}/tasks"
    })


@blueprint.route("/tasks/<pk>", methods=["GET"])
def get_task(pk: int):
    task = Task.get_or_none(Task.id == pk)
    if not task:
        return flask.jsonify({"error": f"No task with given id was found"}), 404

    return flask.jsonify({
        "data": task.to_response(flask.request.base_url),
    }), 200


@blueprint.route('/tasks/<pk>', methods=['PUT'])
def update_task(pk: int):
    attrs = flask.request.json["data"]["attributes"]
    available_for_update = ("title", "image", "command", "description")
    if not all(attr in available_for_update for attr in attrs):
        return flask.jsonify(
            {"error": f"You can update only title, image, command and description fields."}
        ), 400

    exists = (Task
              .select(Task.id)
              .where(Task.id == pk)
              .exists())
    if not exists:
        return flask.jsonify({"error": f"No task with given id was found"}), 404

    Task.update(**attrs).where(Task.id == pk).execute()
    task = Task.get_by_id(Task.id == pk)

    return flask.jsonify({"data": task.to_response(flask.request.base_url)}), 200


@blueprint.route('/tasks/<pk>', methods=["DELETE"])
def delete_task(pk: int):
    task = Task.get_or_none(Task.id == pk)
    if not task:
        return flask.jsonify({"error": f"No task with given id was found"}), 404

    if task.status == Task.Status.running.value:
        return flask.jsonify({"error": "You can't delete running tasks"}), 400

    Task.delete().where(Task.id == pk).execute()
    return {}, 204


@blueprint.route('/tasks', methods=['POST'])
def create_task():
    request_json = flask.request.json
    if "data" not in request_json:
        return flask.jsonify({"error": "data is required"}), 400

    if "attributes" not in request_json["data"]:
        return flask.jsonify({"error": "data.attributes is required"}), 400

    required_attrs = {"title", "command", "image"}
    if not all(attr in request_json["data"]["attributes"] for attr in required_attrs):
        return flask.jsonify({"error": "You didn't pass all required fields. Required: title, command, image"}), 400
    if not is_tasks_amount_under_limit():
        return flask.jsonify({"error": "Tasks amount is over 100. You must delete some before adding new."}), 400

    task = Task(title="")
    task.title = request_json["data"]["attributes"].get("title", "")
    task.command = json.dumps(request_json["data"]["attributes"].get("command", ""))
    task.image = request_json["data"]["attributes"].get("image", "")
    task.description = request_json["data"]["attributes"].get("description", "")
    task.save()

    return flask.jsonify({"data": task.to_response(flask.request.host_url)}), 201


@blueprint.route('/tasks/<pk>/cancel', methods=["POST"])
def cancel_task(pk: int):
    task = Task.get_or_none(Task.id == pk)
    if not task:
        return flask.jsonify({"error": "No task with given id was found"}), 404

    docker_client = DockerClient()
    docker_client.kill_container(task.container_id)
    return flask.jsonify({"success": "The task was canceled"}), 201


@blueprint.route('/tasks/<pk>/logs', methods=['GET'])
def get_task_logs(pk: int):
    task = Task.get_or_none(Task.id == pk)
    if not task:
        return flask.jsonify({"error": "No task with given id was found"}), 404

    return flask.jsonify({"data": {"attributes": {"logs": task.logs}}})
