import uuid

from django.utils import timezone

from twf.models import Task


def generated_task_id():
    """Generate a task ID."""
    security_break = 0

    while True:
        random_id = str(uuid.uuid4())  # Generate a UUID
        if not Task.objects.filter(task_id=random_id).exists():
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
                task_id=generated_task_id())
    task.save()

def save_instant_task_add_dictionary(project, user, text):
    """Save an instant task to the database."""
    title = "Add Dictionary"
    description = "Add a new dictionary to the project."
    save_instant_task(project, user, title, description, text)


def start_related_task(project, user, title, description, text):
    """Start an instant task."""
    task = Task(project=project,
                user=user,
                status='STARTED',
                title=title,
                text=text,
                description=description,
                task_id=generated_task_id())
    task.save()
    return task
