import csv

from django.core.management import BaseCommand

from twf.models import Collection


class Command(BaseCommand):
    """Management command to import dictionaries from a CSV file."""
    help = 'Exports a collection of dictionaries to a CSV file'

    def add_arguments(self, parser):
        """Add arguments to the command"""
        parser.add_argument('collection_id', type=int, help='The project id to create the collection from')

    def handle(self, *args, **options):
        """Handle the command"""
        print("Trying to export data...")
        existing_doc_ids = []
        collection = Collection.objects.get(pk=options['collection_id'])

        songs = []
        for item in collection.items.all()[:2]:
            doc_id = item.document.id
            counter = 1
            while doc_id in existing_doc_ids:
                doc_id + str(counter)
                counter += 1
            existing_doc_ids.append(doc_id)

            song = {
                "doc_id": doc_id,
                "title": item.title,
                "text": ""
            }
            for txt in item.document_configuration["annotations"]:
                song["text"] += txt["text"] + " "
            songs.append(song)

        with open(f"{collection.title}.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(["title", "text"])  # Write the header
            for song in songs:
                writer.writerow([song['title'], song['text']])

        print("Data exported.")