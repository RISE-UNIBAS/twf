"""Task base functions. Functions to start, update, end, and fail tasks."""
import traceback

from django.utils import timezone
from twf.models import Task


def start_task(broker, project, user_id, title="Task Title",
               description="ongoing task", text="Starting Task", percentage_complete=0):
    """Start a new task. Create a new Task object and update the state of the Celery broker.
    :param broker: Celery broker
    :param project: Project object
    :param user_id: User ID
    :param title: Task title
    :param description: Task description
    :param text: Task text
    :param percentage_complete: Percentage complete
    :return: Task object, percentage complete"""
    broker.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                'text': text})
    task = Task.objects.create(project=project,
                               user_id=user_id,
                               title=title,
                               description=description,
                               task_id=broker.request.id, status='STARTED')
    return task, percentage_complete


def update_task(broker, task, text, processed_entries, number_of_entries):
    """Update the task. Update the Task object and update the state of the Celery broker.
    :param broker: Celery broker
    :param task: Task object
    :param text: Task text
    :param processed_entries: Number of processed entries
    :param number_of_entries: Total number of entries
    :return: Task object, percentage complete"""

    percentage_complete = (processed_entries / number_of_entries) * 100
    return update_task_percentage(broker, task, text, percentage_complete)


def update_task_percentage(broker, task, text, percentage_complete):
    """Update the task. Update the Task object and update the state of the Celery broker.
    :param broker: Celery broker
    :param task: Task object
    :param text: Task text
    :param percentage_complete: Percentage complete
    :return: Task object, percentage complete"""

    task.status = 'PROGRESS'
    task.text = text
    task.save()
    broker.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100, 'text': text})

    return task, percentage_complete


def end_task(broker, task, text, description=None, meta=None):
    """End the task. Update the Task object and update the state of the Celery broker.
    :param broker: Celery broker
    :param task: Task object
    :param text: Task text
    :param description: Task description
    :param meta: Task metadata"""

    task.status = 'SUCCESS'
    task.text = text
    if description:
        task.description = description
    task.end_time = timezone.now()
    if meta:
        task.meta = meta
    else:
        task.meta = {}
    task.save()
    broker.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'text': text})


def fail_task(broker, task, text, exception, meta=None):
    """Fail the task and update the task state."""
    task.status = 'FAILURE'
    task.text = text
    task.end_time = timezone.now()
    if meta is None:
        meta = {}

    # Add exception details to metadata
    meta.update({
        'current': 100,
        'total': 100,
        'text': text,
        'exc_type': type(exception).__name__,
        'message': str(exception),
        'traceback': "".join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
    })

    # Save task state and update broker
    task.meta = meta
    task.save()
    broker.update_state(state='FAILURE', meta=meta)
    return task