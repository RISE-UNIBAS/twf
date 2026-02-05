"""Celery tasks for searching entities in dictionaries"""

import traceback

from celery import shared_task

from twf.clients.geonames_client import search_location
from twf.clients.gnd_client import search_gnd
from twf.clients.wikidata_client import search_wikidata_entities
from twf.models import Dictionary, DictionaryEntry
from twf.tasks.task_base import BaseTWFTask


@shared_task(bind=True, base=BaseTWFTask)
def search_gnd_entries(self, project_id, user_id, **kwargs):
    """
    Search GND (German National Library) for all entries in a dictionary.

    Args:
        self: Celery task instance
        project_id: ID of the project
        user_id: ID of the user performing the search
        **kwargs: Additional parameters including:
            - dictionary_id: ID of the dictionary to process
            - earliest_birth_year: Filter results by birth year range
            - latest_birth_year: Filter results by birth year range
            - show_empty: Whether to show results with no birth year

    Returns:
        None (updates dictionary entry metadata with GND data)
    """
    self.validate_task_parameters(
        kwargs,
        ["dictionary_id", "earliest_birth_year", "latest_birth_year", "show_empty"],
    )

    dictionary = Dictionary.objects.get(id=kwargs.get("dictionary_id"))
    self.set_total_items(dictionary.entries.count())

    earliest_birth_year = kwargs.get("earliest_birth_year")
    latest_birth_year = kwargs.get("latest_birth_year")
    show_empty = kwargs.get("show_empty")

    found_entries = 0
    for entry in dictionary.entries.all():
        try:
            # Perform the GND search
            results = search_gnd(
                entry.label,
                earliest_birth_year=earliest_birth_year,
                latest_birth_year=latest_birth_year,
                show_empty=show_empty,
            )

            if results:
                data = results[0]
                entry.metadata["gnd"] = data
                entry.save(current_user=self.user)
                found_entries += 1

            # Update progress
            self.advance_task()
        except Exception as e:
            # Log the exception details
            error_message = f"Error processing entry '{entry.label}': {e}"
            error_traceback = traceback.format_exc()
            print(error_message)  # TODO: Log this to the task log
            print(error_traceback)

            self.end_task(status="FAILURE")

    # Finalize the task
    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_wikidata_entries(self, project_id, user_id, **kwargs):
    """Search for entities using the Wikidata API for all entries in a dictionary"""
    self.validate_task_parameters(kwargs, ["dictionary_id", "entity_type", "language"])

    dictionary = Dictionary.objects.get(id=kwargs.get("dictionary_id"))
    self.set_total_items(dictionary.entries.count())
    entity_type = kwargs.get("entity_type")
    language = kwargs.get("language")

    found_entries = 0
    for entry in dictionary.entries.all():
        # Perform Wikidata search for each entry
        results = search_wikidata_entities(
            query=entry.label, entity_type=entity_type, language=language, limit=5
        )

        if results:
            data = results[0]
            entry.metadata["wikidata"] = data
            entry.save(current_user=self.user)
            found_entries += 1

        # Update the progress
        self.advance_task()

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_geonames_entries(self, project_id, user_id, **kwargs):
    """
    Search Geonames for all entries in a dictionary.

    Args:
        self: Celery task instance
        project_id: ID of the project
        user_id: ID of the user performing the search
        **kwargs: Additional parameters including:
            - dictionary_id: ID of the dictionary to process
            - similarity_threshold: Minimum similarity score for matches
            - country_restriction: Optional country code to restrict results

    Returns:
        None (updates dictionary entry metadata with Geonames data)
    """
    self.validate_task_parameters(
        kwargs, ["dictionary_id", "similarity_threshold", "country_restriction"]
    )

    dictionary = Dictionary.objects.get(id=kwargs.get("dictionary_id"))
    self.set_total_items(dictionary.entries.count())

    geonames_username = self.project.get_credentials("geonames").get("username")
    similarity_threshold = kwargs.get("similarity_threshold")
    country_restriction = kwargs.get("country_restriction")

    if geonames_username == "" or not geonames_username:
        error_message = "Geonames username is required"
        self.end_task(status="FAILURE", error_msg=error_message)
        raise ValueError(error_message)

    if country_restriction == "":
        country_restriction = None

    found_entries = 0
    for entry in dictionary.entries.all():
        # Perform Geonames search for each entry
        try:
            location_info_list = search_location(
                entry.label,
                geonames_username,
                False,
                country_restriction,
                similarity_threshold,
            )

            if location_info_list:
                data, similarity = location_info_list[0]
                entry.metadata["geonames"] = data
                entry.save(current_user=self.user)
                found_entries += 1

            # Update the progress
            self.advance_task()
        except Exception as e:
            self.end_task(status="FAILURE")

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_gnd_entry(self, project_id, user_id, **kwargs):
    """
    Search GND (German National Library) for a single dictionary entry.

    Args:
        self: Celery task instance
        project_id: ID of the project
        user_id: ID of the user performing the search
        **kwargs: Additional parameters including:
            - entry_id: ID of the dictionary entry to search
            - earliest_birth_year: Filter results by birth year range
            - latest_birth_year: Filter results by birth year range
            - show_empty: Whether to show results with no birth year

    Returns:
        None (updates dictionary entry metadata with GND data)
    """
    self.validate_task_parameters(
        kwargs, ["entry_id", "earliest_birth_year", "latest_birth_year", "show_empty"]
    )

    dictionary_entry = DictionaryEntry.objects.get(id=kwargs.get("entry_id"))
    self.set_total_items(1)

    try:
        results = search_gnd(
            dictionary_entry.label,
            earliest_birth_year=kwargs.get("earliest_birth_year"),
            latest_birth_year=kwargs.get("latest_birth_year"),
            show_empty=kwargs.get("show_empty"),
        )
        if results:
            data = results[0]
            dictionary_entry.metadata["gnd"] = data
            dictionary_entry.save(current_user=self.user)
    except Exception as e:
        self.end_task(status="FAILURE")

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_geonames_entry(self, project_id, user_id, **kwargs):
    """
    Search Geonames for a single dictionary entry.

    Args:
        self: Celery task instance
        project_id: ID of the project
        user_id: ID of the user performing the search
        **kwargs: Additional parameters including:
            - entry_id: ID of the dictionary entry to search
            - similarity_threshold: Minimum similarity score for matches
            - country_restriction: Optional country code to restrict results

    Returns:
        None (updates dictionary entry metadata with Geonames data)
    """
    self.validate_task_parameters(
        kwargs, ["entry_id", "similarity_threshold", "country_restriction"]
    )

    dictionary_entry = DictionaryEntry.objects.get(id=kwargs.get("entry_id"))
    self.set_total_items(1)

    geonames_username = self.project.get_credentials("geonames").get("username")
    similarity_threshold = kwargs.get("similarity_threshold")
    country_restriction = kwargs.get("country_restriction")

    if country_restriction == "":
        country_restriction = None

    try:
        location_info_list = search_location(
            dictionary_entry.label,
            geonames_username,
            False,
            country_restriction,
            similarity_threshold,
        )
        if location_info_list:
            data, similarity = location_info_list[0]
            dictionary_entry.metadata["geonames"] = data
            dictionary_entry.save(current_user=self.user)
    except Exception as e:
        self.end_task(status="FAILURE")

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_wikidata_entry(self, project_id, user_id, **kwargs):
    """
    Search Wikidata for a single dictionary entry.

    Args:
        self: Celery task instance
        project_id: ID of the project
        user_id: ID of the user performing the search
        **kwargs: Additional parameters including:
            - entry_id: ID of the dictionary entry to search
            - entity_type: Type of Wikidata entity to search for
            - language: Language code for search results

    Returns:
        None (updates dictionary entry metadata with Wikidata data)
    """
    self.validate_task_parameters(kwargs, ["entry_id", "entity_type", "language"])

    dictionary_entry = DictionaryEntry.objects.get(id=kwargs.get("entry_id"))
    self.set_total_items(1)

    try:
        results = search_wikidata_entities(
            query=dictionary_entry.label,
            entity_type=kwargs.get("entity_type"),
            language=kwargs.get("language"),
            limit=5,
        )
        if results:
            data = results[0]
            dictionary_entry.metadata["wikidata"] = data
            dictionary_entry.save(current_user=self.user)
    except Exception as e:
        self.end_task(status="FAILURE")

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_ai_entries(self, project_id, user_id, **kwargs):
    """
    Unified task for AI batch processing of dictionary entries.

    Supports any AI provider through the generic AI client.

    Args:
        project_id: Project ID
        user_id: User ID
        **kwargs: Must include:
            - dictionary_id: ID of the dictionary to process
            - ai_provider: Provider key ('openai', 'genai', 'anthropic', 'mistral', etc.)
            - model: Model name to use
            - prompt: The prompt template
            - role_description: System role description
    """
    self.validate_task_parameters(
        kwargs, ["dictionary_id", "ai_provider", "model", "prompt", "role_description"]
    )

    dictionary = Dictionary.objects.get(id=kwargs.get("dictionary_id"))
    provider = kwargs.get("ai_provider")

    # Map provider keys to the keys expected by process_ai_request
    # (genai->genai, anthropic->anthropic, etc. - they happen to match)
    self.process_ai_request(
        dictionary.entries.all(),
        provider,
        kwargs["prompt"],
        kwargs["role_description"],
        provider,
        model=kwargs.get("model"),
    )


@shared_task(bind=True, base=BaseTWFTask)
def search_ai_entry(self, project_id, user_id, **kwargs):
    """
    Unified task for AI request (supervised) processing of a single dictionary entry.

    Supports any AI provider through the generic AI client.

    Args:
        project_id: Project ID
        user_id: User ID
        **kwargs: Must include:
            - entry_id: ID of the dictionary entry to process
            - ai_provider: Provider key ('openai', 'genai', 'anthropic', 'mistral', etc.)
            - model: Model name to use
            - prompt: The prompt template
            - role_description: System role description
    """
    self.validate_task_parameters(
        kwargs, ["entry_id", "ai_provider", "model", "prompt", "role_description"]
    )

    dictionary_entry = DictionaryEntry.objects.get(id=kwargs.get("entry_id"))
    provider = kwargs.get("ai_provider")

    self.process_ai_request(
        [dictionary_entry],
        provider,
        kwargs["prompt"],
        kwargs["role_description"],
        provider,
        model=kwargs.get("model"),
    )
