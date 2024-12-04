"""Celery tasks for searching entities in dictionaries"""
import traceback

from celery import shared_task

from twf.clients.geonames_client import search_location
from twf.clients.gnd_client import search_gnd
from twf.clients.simple_ai_clients import AiApiClient
from twf.clients.wikidata_client import search_wikidata_entities
# from twf.clients.wikidata_client import query_wikidata
from twf.models import Dictionary, User, Project
from twf.tasks.task_base import start_task, update_task, end_task, fail_task


def get_dictionary_and_user(broker, task, dictionary_id, user_id):
    """Get the dictionary and user objects
    :param broker: Celery broker
    :param task: Task object
    :param dictionary_id: Dictionary ID
    :param user_id: User ID"""
    try:
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)
        number_of_entries = dictionary.entries.count()
        return dictionary, user, number_of_entries
    except Dictionary.DoesNotExist as e:
        fail_task(broker, task, f"Dictionary not found: {dictionary_id}", e)
    except User.DoesNotExist as e:
        fail_task(broker, task, f"User not found: {user_id}", e)
    except Exception as e:
        fail_task(broker, task, f"NBot found dict={dictionary_id}, user={user_id}", e)


@shared_task(bind=True)
def search_gnd_entries(self, project_id, dictionary_id, user_id,
                       earliest_birth_year, latest_birth_year, show_empty):
    """ Search for entities using the GND API for all entries in a dictionary"""
    project = Project.objects.get(id=project_id)
    task, percentage_complete = start_task(self, project, user_id, text="Starting GND Search...",
                                           title="Dictionary GND Search")

    dictionary, user, number_of_entries = get_dictionary_and_user(self, task, dictionary_id, user_id)
    processed_entries = 0
    found_entries = 0
    for entry in dictionary.entries.all():
        try:
            # Log the entry being processed
            print(f"Processing entry: {entry.label} with range {earliest_birth_year}-{latest_birth_year}")

            # Perform the GND search
            results = search_gnd(entry.label,
                                 earliest_birth_year=earliest_birth_year, latest_birth_year=latest_birth_year,
                                 show_empty=show_empty)

            if results:
                data = results[0]
                entry.authorization_data['gnd'] = data
                entry.save(current_user=user)
                found_entries += 1

            # Update progress
            processed_entries += 1
            task, percentage_complete = update_task(self, task,
                                                    f'GND Search in progress for entry {entry.label}...',
                                                    processed_entries, number_of_entries)
        except Exception as e:
            # Log the exception details
            error_message = f"Error processing entry '{entry.label}': {e}"
            error_traceback = traceback.format_exc()
            print(error_message)
            print(error_traceback)

            # Mark task as failed for this entry
            fail_task(self, task, error_message, e)

    # Finalize the task
    end_task(self, task, 'GND Search Completed.',
             description=f'GND Search for all entries in the dictionary "{dictionary.label}". '
                         f'Found {found_entries} entries.')


@shared_task(bind=True)
def search_wikidata_entries(self, project_id, dictionary_id, user_id, entity_type, language):
    """ Search for entities using the Wikidata API for all entries in a dictionary"""
    project = Project.objects.get(id=project_id)
    task, percentage_complete = start_task(self, project, user_id, text="Starting Wikidata Search...",
                                           title="Dictionary Wikidata Search")

    dictionary, user, number_of_entries = get_dictionary_and_user(self, task, dictionary_id, user_id)
    number_of_entries = dictionary.entries.count()
    processed_entries = 0
    found_entries = 0
    for entry in dictionary.entries.all():
        # Perform Wikidata search for each entry
        results = search_wikidata_entities(query=entry.label, entity_type=entity_type, language=language, limit=5)

        if results:
            data = results[0]
            entry.authorization_data['wikidata'] = data
            entry.save(current_user=user)
            found_entries += 1

        # Update the progress
        processed_entries += 1
        task, percentage_complete = update_task(self, task, f'Wikidata Search in progress for entry {entry.label}...',
                                                processed_entries, number_of_entries)

    end_task(self, task, 'Wikidata Search Completed.',
             description=f'Wikidata Search for all entries in the dictionary "{dictionary.label}". '
                         f'Found {found_entries} entries.')


@shared_task(bind=True)
def search_geonames_entries(self, project_id, dictionary_id, user_id, geonames_username,
                            country_restriction, similarity_threshold):
    """ Search for locations using the GeoNames API for all entries in a dictionary"""
    project = Project.objects.get(id=project_id)
    task, percentage_complete = start_task(self, project, user_id, text="Starting Geonames Search...",
                                           title="Dictionary Geonames Search")

    dictionary, user, number_of_entries = get_dictionary_and_user(self, task, dictionary_id, user_id)
    if country_restriction == '':
        country_restriction = None

    completed_entries = 0
    found_entries = 0
    for entry in dictionary.entries.all():
        # Perform Geonames search for each entry
        try:
            completed_entries += 1
            location_info_list = search_location(entry.label, geonames_username, False,
                                                 country_restriction, similarity_threshold)

            if location_info_list:
                data, similarity = location_info_list[0]
                entry.authorization_data['geonames'] = data
                entry.save(current_user=user)
                found_entries += 1

            # Update the progress
            task, percentage_complete = update_task(self, task,
                                                    f'Geonames Search in progress for entry {entry.label}...',
                                                    completed_entries, number_of_entries)
        except Exception as e:
            fail_task(self, task, str(e), e)

    end_task(self, task, f'Geonames Search Completed. Found {found_entries} entries.',
             description=f'Geonames Search for all entries in the dictionary "{dictionary.label}". '
                         f'Found {found_entries} entries.')


@shared_task(bind=True)
def search_openai_entries(self, project_id, dictionary_id, user_id, prompt):
    project = Project.objects.get(id=project_id)
    """ Search for entities using the Openai API for all entries in a dictionary
    :param self: Celery task object
    :param project_id: Project ID
    :param dictionary_id: Dictionary ID
    :param user_id: User ID
    :param prompt: Openai prompt template"""
    task, percentage_complete = start_task(self, project, user_id, text="Starting Openai Search...",
                                           title="Dictionary Openai Search")

    client = AiApiClient('openai', project.get_credentials('openai').get('api_key'))

    dictionary, user, number_of_entries = get_dictionary_and_user(self, task, dictionary_id, user_id)
    processed_entries = 0
    for entry in dictionary.entries.all():
        # Perform Openai search for each entry
        answer, elapsed_time = client.prompt(
            model=project.get_credentials('openai').get('default_model'),
            prompt=prompt.format(label=entry.label)
        )

        # Save the answer to the entry
        entry.authorization_data['openai'] = answer.choices[0].message.to_json()
        entry.save(current_user=user)

        # Update the progress
        task, percentage_complete = update_task(self, task, f'Openai Search in progress for entry {entry.label}...',
                                                processed_entries, number_of_entries)
        processed_entries += 1

    end_task(self, task, 'Openai Search Completed.',
             description=f'Openai Search for all entries in the dictionary "{dictionary.label}". '
                         f'Found {processed_entries} entries.')  # TODO: Add the number of found entries


@shared_task(bind=True)
def search_gnd_entry(self, project_id, dictionary_id, user_id,
                     earliest_birth_year, latest_birth_year, show_empty):
    """Search for a single entry in the GND API"""
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform GND search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'GND Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e)) from e
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e)) from e
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e)) from e


@shared_task(bind=True)
def search_geonames_entry(self, project, dictionary_id, user_id):
    """Search for a single entry in the Geonames API"""
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform Geonames search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'Geonames Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e)) from e
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e)) from e
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e)) from e


@shared_task(bind=True)
def search_wikidata_entry(self, project, dictionary_id, user_id):
    """Search for a single entry in the Wikidata API"""
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform Wikidata search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'Wikidata Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e)) from e
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e)) from e
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e)) from e


@shared_task(bind=True)
def search_openai_entry(self, project, dictionary_id, user_id):
    """Search for a single entry in the Openai API"""
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform Openai search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'Openai Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e)) from e
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e)) from e
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e)) from e
