from .database import Task

TASKS_COUNT_LIMIT = 100


def is_tasks_amount_under_limit():
    count = Task.select(Task.id).count()
    return count < TASKS_COUNT_LIMIT


# def time_limit(func):
#     def wrapper(limit=10):
#         func()
#         while limit > 0:
#
#
#
#     return wrapper