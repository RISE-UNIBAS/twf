from celery import shared_task

from twf.clients.geonames_client import search_location
# from twf.clients.wikidata_client import query_wikidata
from twf.models import Dictionary, User


def get_dictionary_and_user(dictionary_id, user_id):
    try:
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)
        number_of_entries = dictionary.entries.count()
        return dictionary, user, number_of_entries
    except Dictionary.DoesNotExist as e:
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        raise ValueError(str(e))
    except Exception as e:
        raise ValueError(str(e))


@shared_task(bind=True)
def search_gnd_entries(self, dictionary_id, user_id):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting GND Search...'})

    dictionary, user, number_of_entries = get_dictionary_and_user(dictionary_id, user_id)
    for entry in dictionary.entries.all():
        # Perform GND search for each entry

        # Update the progress
        percentage_complete = (entry.id / number_of_entries) * 100
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': f'GND Search in progress for entry {entry.id}...'})

    percentage_complete = 100
    self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                            'text': 'GND Search Completed.'})


@shared_task(bind=True)
def search_wikidata_entries(self, dictionary_id, user_id, entity_type, language):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Wikidata Search...'})

    dictionary, user, number_of_entries = get_dictionary_and_user(dictionary_id, user_id)

    number_of_entries = dictionary.entries.count()
    for entry in dictionary.entries.all():
        # Perform Wikidata search for each entry
        results = {} # query_wikidata(entity_type, entry.label, language)

        # Update the progress
        percentage_complete = (entry.id / number_of_entries) * 100
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': f'GND Search in progress for entry {entry.id}...'})

    percentage_complete = 100
    self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                             'text': 'Wikidata Search Completed.'})


@shared_task(bind=True)
def search_geonames_entries(self, dictionary_id, user_id, geonames_username, country_restriction, similarity_threshold):
    """ Search for locations using the GeoNames API for all entries in a dictionary"""
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Geonames Search...'})

    dictionary, user, number_of_entries = get_dictionary_and_user(dictionary_id, user_id)
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
            percentage_complete = (completed_entries / number_of_entries) * 100
            self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                      'text': f'Geonames Search in progress for entry {entry.label}...'})
        except Exception as e:
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise ValueError(str(e))

    percentage_complete = 100
    self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                             'text': 'Geonames Search Completed. Found entries: ' + str(found_entries)})


@shared_task(bind=True)
def search_openai_entries(self, dictionary_id, user_id):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Openai Search...'})

    dictionary, user, number_of_entries = get_dictionary_and_user(dictionary_id, user_id)

    for entry in dictionary.entries.all():
        # Perform Openai search for each entry

        # Update the progress
        percentage_complete = (entry.id / number_of_entries) * 100
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': f'GND Search in progress for entry {entry.id}...'})

    percentage_complete = 100
    self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                             'text': 'GND Search Completed.'})


@shared_task(bind=True)
def search_gnd_entry(self, dictionary_id, user_id):
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform GND search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'GND Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e))


@shared_task(bind=True)
def search_geonames_entry(self, dictionary_id, user_id):
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform Geonames search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'Geonames Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e))


@shared_task(bind=True)
def search_wikidata_entry(self, dictionary_id, user_id):
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform Wikidata search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'Wikidata Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e))


@shared_task(bind=True)
def search_openai_entry(self, dictionary_id, user_id):
    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        # Perform Openai search for the entry

        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100,
                                                 'text': 'Openai Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise ValueError(str(e))