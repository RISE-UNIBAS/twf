import csv
import pandas as pd

from django.db import transaction
from .models import Dictionary, DictionaryEntry, Variation


def import_dictionary_from_csv(csv_file_path, type_name, label,
                               label_column='preferred_name', variations_column='variations'):

    df = pd.read_csv(csv_file_path, encoding='utf-8')

    dictionary = Dictionary.objects.create(label=label, type=type_name)

    # Create dictionary entries
    for index, row in df.iterrows():
        entry = DictionaryEntry.objects.create(dictionary=dictionary, label=row[label_column])
        variations = row[variations_column].split(',')
        for variation in variations:
            if variation != '':
                if not Variation.objects.filter(entry=entry, variation=variation).exists():
                    Variation.objects.create(entry=entry, variation=variation)
                else:
                    print(f"Skipping duplicate variation for entry {entry.label}")

            else:
                print(f"Skipping empty variation for entry {entry.label}")