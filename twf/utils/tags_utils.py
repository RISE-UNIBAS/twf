import json

from django.db.models import Count
from fuzzywuzzy import process

from twf.models import PageTag, Variation


def get_translated_tag_type(project, tag_type):
    task_configurations = project.get_task_configuration("tag_types")
    if "tag_type_translator" not in task_configurations:
        return tag_type

    tag_type_translator = json.loads(task_configurations["tag_type_translator"])
    if tag_type in tag_type_translator:
        return tag_type_translator[tag_type]


def get_all_tag_types(project):
    """Get the distinct tag types."""
    distinct_variation_types = (
        PageTag.objects.filter(page__document__project=project)
        .exclude(variation_type__in=get_excluded_types(project))
        .exclude(variation_type__in=get_date_types(project))
        .values('variation_type')
        .annotate(count=Count('variation_type'))
        .order_by('variation_type')
    )

    # Extracting the distinct variation types from the queryset
    distinct_variation_types_list = [item['variation_type'] for item in distinct_variation_types]
    return distinct_variation_types_list

def get_excluded_types(project):
    """Get the excluded tag types."""
    task_configurations = project.get_task_configuration("tag_types")
    if "ignored_tag_types" in task_configurations:
        conf = json.loads(task_configurations["ignored_tag_types"])
        if "excluded" in conf:
            return conf["excluded"]
        return []
    return []

def get_date_types(project):
    """Get the date tag types."""
    task_configurations = project.get_task_configuration("tag_types")
    if "ignored_tag_types" in task_configurations:
        conf = json.loads(task_configurations["ignored_tag_types"])
        if "dates" in conf:
            return conf["dates"]
        return []
    return []


def get_closest_variations(page_tag):
    """Return the 5 closest variations to the tag."""
    dict_type = page_tag.variation_type
    dict_type = get_translated_tag_type(page_tag.page.document.project, dict_type)

    variations = Variation.objects.filter(
        entry__dictionary__in=page_tag.page.document.project.selected_dictionaries.all(),
        entry__dictionary__type=dict_type)
    variations_list = [variation.variation for variation in variations]

    # Using fuzzywuzzy to find the top 5 closest matches
    top_matches = process.extract(page_tag.variation, variations_list, limit=5)

    # Retrieve the matched Variation objects
    closest_variations = []
    for match in top_matches:
        variation_text, score = match
        matched_variation = variations.filter(variation=variation_text).first()
        if matched_variation:
            closest_variations.append((matched_variation, score))

    return closest_variations


def assign_tag(page_tag, user):
    """Assign the tag to a dictionary entry."""
    tag_type_translator = page_tag.page.document.project.get_task_configuration('tag_types').get('tag_type_translator', {})
    try:
        dictionary_type = page_tag.variation_type
        if tag_type_translator.get(dictionary_type):
            dictionary_type = tag_type_translator[dictionary_type]
        try:
            entry = Variation.objects.get(
                variation=page_tag.variation,
                entry__dictionary__in=page_tag.page.document.project.selected_dictionaries.all(),
                entry__dictionary__type=dictionary_type)
        except Variation.MultipleObjectsReturned:
            # TODO: Handle multiple objects returned
            entry = Variation.objects.filter(
                variation=page_tag.variation,
                entry__dictionary__in=page_tag.page.document.project.selected_dictionaries.all(),
                entry__dictionary__type=dictionary_type).first()

        page_tag.dictionary_entry = entry.entry
        page_tag.save(current_user=user)
        return True
    except Variation.DoesNotExist:
        return False