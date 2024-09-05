import json

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from twf.models import Collection, Project, CollectionItem, Page, Document


class Command(BaseCommand):
    """Management command to import dictionaries from a CSV file."""
    help = 'Imports PAGE metadata from a CSV file'

    def add_arguments(self, parser):
        """Add arguments to the command"""
        parser.add_argument('project_id', type=int, help='The project id to create the collection from')
        parser.add_argument('user_id', type=int, help='The user id to create the collection for')
        parser.add_argument('data_file', type=str, help='The data file to import')
        parser.add_argument('identifier', type=str, help='The identifier of the data')

    def handle(self, *args, **options):
        print("Trying to import data...")

        project = Project.objects.get(pk=options['project_id'])
        user = User.objects.get(pk=options['user_id'])

        # Read data from file (must be a list of json objects)
        with open(options['data_file'], 'r') as f:
            data = json.load(f)

        for item in data:
            for key, value in item.items():
                try:
                    document = Document.objects.get(document_id=key)
                    document.metadata = {'pages': []}
                    for document_data in value:
                        #
                        for page_id, page_data in document_data.items():
                            tk_page_number = int(page_id.split('/')[-1])
                            try:
                                page = Page.objects.get(document=document, tk_page_number=tk_page_number)
                                page.metadata = page_data
                                page.save(current_user=user)
                                print(f"Page {tk_page_number} updated.")
                                document.metadata['pages'].append(page_data)
                            except Page.DoesNotExist:
                                print(f"Page {tk_page_number} not found.")
                                pass

                    document.save(current_user=user)
                    print(f"Document {key} updated.")

                except Document.DoesNotExist:
                    print(f"Document {key} not found.")
                    pass

        """
        for item in keyed_data.keys():
            try:
                tk_id, tk_page = item.split('/')
                page = Page.objects.get(document__document_id=tk_id, tk_page_number=tk_page)
                page.metadata = keyed_data[item]
                page.save(current_user=user)
                print(f"Page {tk_id} updated.")
            except Page.DoesNotExist:
                print(f"Page {tk_id} not found.")
        """
        # pages = Page.objects.filter(document__project=project)
        # for p in pages:
            # p.metadata = {}
            # p.save()
