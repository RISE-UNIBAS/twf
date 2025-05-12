import uuid
from django.utils import timezone
from twf.models import Task


def generated_task_id():
    """Generate a task ID."""
    security_break = 0

    while True:
        random_id = str(uuid.uuid4())  # Generate a UUID
        if not Task.objects.filter(celery_task_id=random_id).exists():
            return random_id
        security_break += 1
        if security_break > 100:
            return None


def save_instant_task(project, user, title, description, text):
    """Save an instant task to the database."""
    task = Task(project=project,
                user=user,
                status='SUCCESS',
                title=title,
                text=text,
                description=description,
                end_time=timezone.now(),
                celery_task_id=generated_task_id())
    task.save()


def save_instant_task_add_dictionary(project, user, text):
    """Save an instant task to the database."""
    title = "Add Dictionary"
    description = "Add a new dictionary to the project."
    save_instant_task(project, user, title, description, text)


def save_instant_task_create_project(project, user):
    """Save an instant task to the database."""
    title = "Create Project"
    description = "Create a project"
    save_instant_task(project, user, title, description, "The project was created.")


def save_instant_task_request_transkribus_export(project, user, text):
    """Save an instant task to the database."""
    title = "Request Transkribus Export"
    description = "Request an export of the project data from Transkribus."
    save_instant_task(project, user, title, description, text)


def save_instant_task_transkribus_export_download(project, user, text):
    """Save an instant task to the database."""
    title = "Download Transkribus Export"
    description = "Download the exported data from Transkribus."
    save_instant_task(project, user, title, description, text)


def save_instant_task_delete_all_documents(project, user):
    """Save an instant task to the database."""
    title = "Delete All Documents"
    description = "Delete all documents in the project."
    save_instant_task(project, user, title, description, "All documents were deleted.")


def save_instant_task_delete_all_tags(project, user):
    """Save an instant task to the database."""
    title = "Delete All Tags"
    description = "Delete all tags in the project."
    save_instant_task(project, user, title, description, "All tags were deleted.")


def save_instant_task_delete_all_collections(project, user):
    """Save an instant task to the database."""
    title = "Delete All Collections"
    description = "Delete all collections in the project."
    save_instant_task(project, user, title, description, "All collections were deleted.")


def save_instant_task_unpark_all_tags(project, user):
    """Save an instant task to the database."""
    title = "Unpark All Tags"
    description = "Unpark all tags in the project."
    save_instant_task(project, user, title, description, "All tags were unparked.")


def save_instant_task_remove_all_prompts(project, user):
    """Save an instant task to the database."""
    title = "Remove All Prompts"
    description = "Remove all prompts in the project."
    save_instant_task(project, user, title, description, "All prompts were removed.")


def save_instant_task_remove_all_tasks(project, user):
    """Save an instant task to the database."""
    title = "Remove All Tasks"
    description = "Remove all tasks in the project."
    save_instant_task(project, user, title, description, "All tasks were removed.")


def save_instant_task_remove_all_dictionaries(project, user):
    """Save an instant task to the database."""
    title = "Remove All Dictionaries"
    description = "Remove all dictionaries from the project."
    save_instant_task(project, user, title, description, "All dictionaries were removed from the project.")


def start_related_task(project, user, title, description, text):
    """Start an instant task."""
    task = Task(project=project,
                user=user,
                status='STARTED',
                title=title,
                text=text,
                description=description,
                celery_task_id=generated_task_id())
    task.save()
    return task
