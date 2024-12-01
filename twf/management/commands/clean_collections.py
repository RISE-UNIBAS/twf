"""Management command to clean collections."""
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from twf.models import Collection, Project


class Command(BaseCommand):
    """Management command to clean collections."""
    help = 'Management command to clean collections.'

    def add_arguments(self, parser):
        """Add arguments to the command"""
        parser.add_argument('project_id', type=int, help='The project id to create the collection from')
        parser.add_argument('user_id', type=int, help='The user id to create the collection for')

    def handle(self, *args, **options):
        """Handle the command"""
        print("Trying to create a song collection...")

        project = Project.objects.get(pk=options['project_id'])
        user = User.objects.get(pk=options['user_id'])

        collections = Collection.objects.filter(project=project)
        collections.delete()
