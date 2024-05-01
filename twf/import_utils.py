""" This module contains utility functions for importing data into the database."""
import pandas as pd

from .models import Dictionary, DictionaryEntry, Variation


def import_dictionary_from_csv(csv_file_path, type_name, label,
                               label_column='preferred_name', variations_column='variations'):
    """
    Import a dictionary from a CSV file.
    :param csv_file_path:       The path to the CSV file.
    :param type_name:           The type of the dictionary.
    :param label:               The label of the dictionary.
    :param label_column:        The name of the column containing the labels.
    :param variations_column:   The name of the column containing the variations.
    :return:
    """

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
