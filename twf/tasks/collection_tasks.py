from celery import shared_task

from twf.tasks.task_base import start_task, end_task


@shared_task(bind=True)
def create_collection(self, project, user_id):
    """ Create a collection for a project """
    task, percentage_complete = start_task(self, project, user_id, text="Starting Collection Creation...",
                                           title="Create Collection")

    end_task(self, task, 'Collection created',
             description=f'Collection created for project {project.name}')
