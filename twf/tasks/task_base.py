"""Task base functions. Functions to start, update, end, and fail tasks."""
import traceback

from django.utils import timezone
from celery import Task as CeleryTask

from twf.clients.simple_ai_clients import AiApiClient
from twf.models import Task, Project, User


class BaseTWFTask(CeleryTask):
    """Base task for all TWF Celery tasks."""

    def before_start(self, task_id, args, kwargs):
        """Initialize project and user before the task starts."""

        self.task_id = task_id
        self.get_project_and_user(args[0], args[1])

        self.task_params = kwargs

        self.total_items = None
        self.processed_items = 0

        # Create a new task object in the database
        self.twf_task = Task.objects.create(
            celery_task_id=task_id,
            project=self.project,
            user=self.user,
            status="STARTED",
            title=self.name,  # Defaults to the task name
        )

    @staticmethod
    def validate_task_parameters(kwargs, required_params):
        """Ensure all required parameters are present in kwargs."""
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

    def get_project_and_user(self, project_id, user_id):
        """Fetch project and user from the database."""
        if not project_id or not user_id:
            raise ValueError("Project ID and User ID are required")

        try:
            self.project = Project.objects.get(pk=project_id)
            self.user = User.objects.get(pk=user_id)
        except Project.DoesNotExist:
            raise ValueError(f"Project with ID {project_id} not found")
        except User.DoesNotExist:
            raise ValueError(f"User with ID {user_id} not found")

    def set_total_items(self, total):
        """Set the total number of items for progress calculation."""
        self.total_items = total
        self.processed_items = 0  # Reset counter

    def advance_task(self):
        if self.total_items is not None and self.total_items > 0:
            self.processed_items += 1  # Increment processed count
            progress = int((self.processed_items / self.total_items) * 100)
            self.update_progress(progress)

    def update_progress(self, progress):
        """Update task progress in the database."""
        if self.twf_task:
            self.twf_task.progress = progress
            self.twf_task.save(update_fields=["progress"])

    def process_ai_request(self, items, client_name, prompt, role_description, metadata_field):
        """Generalized function to process AI requests for multiple items."""
        self.set_total_items(len(items))
        self.create_configured_client(client_name, role_description)

        for item in items:
            response_dict, elapsed_time = self.prompt_client(item, prompt)
            item.metadata[metadata_field] = response_dict
            item.save(current_user=self.user)
            self.advance_task()

        self.end_task()

    def end_task(self, status="SUCCESS"):
        """Mark the task as completed or failed."""
        if self.twf_task:
            self.twf_task.status = status
            self.twf_task.save(update_fields=["status"])

    def create_configured_client(self, client_name, role_description):
        self.client_name = client_name
        self.credentials = self.project.get_credentials(client_name)
        self.client = AiApiClient(api=client_name,
                                  api_key=self.credentials['api_key'],
                                  gpt_role_description=role_description)

    def prompt_client(self, item, prompt):
        context = item.get_text()
        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = self.client.prompt(model=self.credentials['default_model'],
                                                    prompt=prompt)
        response_dict = response.to_dict()
        return response_dict, elapsed_time


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

    task_meta = {'current': 100, 'total': 100, 'text': text}
    if "download_url" in task.meta:
        task_meta["download_url"] = task.meta["download_url"]

    broker.update_state(state='SUCCESS', meta=task_meta)


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