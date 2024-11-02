from twf.models import Dictionary, PageTag


def get_dictionary_json_data(dictionary_id):
    """Get the JSON data for the dictionary."""
    dictionary = Dictionary.objects.get(pk=dictionary_id)

    json_data = {
        "name": dictionary.label,
        "type": dictionary.type,
        "metadata": {},
        "entries": []
    }

    entries = dictionary.entries.all()
    for entry in entries:
        json_data["entries"].append(
            {
                "label": entry.label,
                "variations": list(entry.variations.all().values_list('variation', flat=True))
            }
        )
    return json_data


def get_dictionary_csv_data(pk):
    csv_data = 'entry;variations\n'
    dictionary = Dictionary.objects.get(pk=pk)
    entries = dictionary.entries.all()
    for entry in entries:
        csv_data += f'{entry.label};'
        variations = entry.variations.all()
        for variation in variations:
            csv_data += f'{variation.variation},'
        csv_data += '\n'
    return csv_data


def get_tags_json_data(project_id):
    """Get the JSON data for the tags."""
    tags = PageTag.objects.filter(page__document__project_id=project_id)

    json_data = {
        "entries": []
    }

    for entry in tags:
        json_data["entries"].append(
            {
                "label": entry.variation,
            }
        )
    return json_data


def get_tags_csv_data(project_id):
    csv_data = 'entry\n'
    tags = PageTag.objects.filter(page__document__project_id=project_id)
    for tag in tags:
        csv_data += f'{tag.variation}\n'
    return csv_data

