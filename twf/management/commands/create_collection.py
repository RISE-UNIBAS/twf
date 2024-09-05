from django.contrib.auth.models import User
from django.core.management import BaseCommand

from twf.models import Collection, Project, CollectionItem


class Command(BaseCommand):
    """Management command to import dictionaries from a CSV file."""
    help = 'Imports dictionaries from a CSV file'

    def add_arguments(self, parser):
        """Add arguments to the command"""
        parser.add_argument('project_id', type=int, help='The project id to create the collection from')
        parser.add_argument('user_id', type=int, help='The user id to create the collection for')

    def handle(self, *args, **options):
        """Handle the command"""
        print("Trying to create a song collection...")

        project = Project.objects.get(pk=options['project_id'])
        user = User.objects.get(pk=options['user_id'])

        try:
            collection = Collection.objects.get(title="Songs", project=project)
            print("Collection already exists. Cleaning up...")
            collection.items.all().delete()
        except Collection.DoesNotExist:
            collection = Collection(title="Songs", description="A collection of songs", project=project)
            collection.save(current_user=user)
            print("Collection created.")

        for document in project.documents.filter(project=project)[:10]:
            print(">>>>>>> Document: ", document, document.document_id)
            collection_item = CollectionItem(collection=collection,
                                             document_configuration={'annotations': []},
                                             document=document)

            for page in document.get_active_pages():
                annotations = page.get_annotations()
                anno_types = []
                for annotation in annotations:
                    anno_types.append(annotation['type'])
                    if annotation['type'] in ['lyrics', 'music', 'heading']:
                        collection_item.document_configuration['annotations'].append(annotation)

            collection_item.title = f'Song in {document.document_id}'
            collection_item.save(current_user=user)
            print(f"Added Song for document {document.document_id} with {len(collection_item.document_configuration['annotations'])} annotations.")