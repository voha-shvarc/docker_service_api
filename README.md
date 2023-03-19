## Timing

We ask to spend not more than 4 hours on the coding task. If you finished earlier - it is great.
But if you reached the time deadline, please outline the strategy and next steps that you're planning
to do.


## Prerequisites

[Install Docker](https://docs.docker.com/install/).

Install GNU Make.

Run the application:
```sh
make run
```

## The Exercise

This repository includes an example API application built with [Flask](https://palletsprojects.com/p/flask/).
For the data layer we use [peewee](http://docs.peewee-orm.com/en/latest/) ORM.
Application also requires [docker](https://docs.docker.com/engine/install/) installed on the machine.

The API interface is described in [OpenAPI 3](https://swagger.io/docs/specification/about/) format in
the [openapi.yaml](./static/openapi.yaml) file. The API semantics is based on [json-api](https://jsonapi.org/) specification.

This API documentation is accessible by the [app index url](http://127.0.0.1:5000/) as
soon as you've started the app.

### Objective

Your goal is to finalize the API that is described in the OpenAPI 3 document.

This work includes fixing and updating the existing code as well as implementing some new features.

You are also welcome to make any changes to the OpenAPI 3 spec that you deem
appropriate. Just make sure all the required functionality is still
present and the final implementation and spec match.

### API Description

We build a service for executing tasks inside the docker container.
The customer could create and execute the task with a command
Examples:
```http request
POST http://127.0.0.1:5000/tasks
Content-Type: application/json

{
  "data": {
    "attributes": {
      "title": "hello world ubuntu",
      "description": "Run hello world in ubuntu",
      "command": "echo hello world",
      "image": "ubuntu"
    }
  }
}
```

Get logs
```http request
GET /tasks/{id}/logs
```

### Feature Requirements

 - CRUD operations for tasks:
   - Do your own best judgement over what fields could be updated
   - Running task could not be deleted
 - Operation to get a task logs.
 - Task command must be executed inside the docker container
 - Task status should be updated according to the command execution status.
 - All tasks must be running in the background and not blocking the API server (See app/worker.py)
 ### Constraints
 
 - At most 100 tasks could be created, API should not allow to create more without deleting any existing tasks before.
 - At most 2 concurrent tasks could run at any given moment. Tasks should be handled in a FIFO manner.
 - Cover most important parts of your code with tests.
 - Valid OpenAPI specification.

### Tests

```python
pytest tests
```

### Extra Questions (If you have a time)

- If we need to limit task in compute resources: e.g. CPU / Memory, how would you do it?
- How to limit task execution time?
- How would you approach task cancellation?
- How would you add authorization to the API? What authz type would you pick and why?
- What kind of test levels do you think this system needs and why?
- When you'll be ready to ship this code to production, how would you deploy it?
