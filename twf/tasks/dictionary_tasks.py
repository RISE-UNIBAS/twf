from celery import shared_task

from twf.models import Dictionary, User


@shared_task(bind=True)
def search_gnd_entries(self, dictionary_id, user_id):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting GND Search...'})

    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        number_of_entries = dictionary.entries.count()
        for entry in dictionary.entries.all():
            # Perform GND search for each entry

            # Update the progress
            percentage_complete = (entry.id / number_of_entries) * 100
            self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                      'text': f'GND Search in progress for entry {entry.id}...'})

        percentage_complete = 100
        self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                                'text': 'GND Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


@shared_task(bind=True)
def search_wikidata_entries(self, dictionary_id, user_id):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Wikidata Search...'})

    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        number_of_entries = dictionary.entries.count()
        for entry in dictionary.entries.all():
            # Perform Wikidata search for each entry

            # Update the progress
            percentage_complete = (entry.id / number_of_entries) * 100
            self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                      'text': f'GND Search in progress for entry {entry.id}...'})

        percentage_complete = 100
        self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                                 'text': 'Wikidata Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


@shared_task(bind=True)
def search_geonames_entries(self, dictionary_id, user_id):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Geonames Search...'})

    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        number_of_entries = dictionary.entries.count()
        for entry in dictionary.entries.all():
            # Perform GND search for each entry

            # Update the progress
            percentage_complete = (entry.id / number_of_entries) * 100
            self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                      'text': f'Geonames Search in progress for entry {entry.id}...'})

        percentage_complete = 100
        self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                                 'text': 'Geonames Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


@shared_task(bind=True)
def search_openai_entries(self, dictionary_id, user_id):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Openai Search...'})

    try:
        # Fetch the dictionary
        dictionary = Dictionary.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)

        number_of_entries = dictionary.entries.count()
        for entry in dictionary.entries.all():
            # Perform Openai search for each entry

            # Update the progress
            percentage_complete = (entry.id / number_of_entries) * 100
            self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                      'text': f'GND Search in progress for entry {entry.id}...'})

        percentage_complete = 100
        self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                                 'text': 'GND Search Completed.'})
    except Dictionary.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "Dictionary not found"})
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': "User not found"})
        raise ValueError(str(e))
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


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