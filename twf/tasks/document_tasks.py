from celery import shared_task

from twf.clients.geonames_client import search_location
from twf.clients.simple_ai_clients import AiApiClient
# from twf.clients.wikidata_client import query_wikidata
from twf.models import Dictionary, User, Project


def get_project_and_user(dictionary_id, user_id):
    try:
        project = Project.objects.get(id=dictionary_id)
        user = User.objects.get(id=user_id)
        number_of_documents = project.entries.count()
        return project, user, number_of_documents
    except Dictionary.DoesNotExist as e:
        raise ValueError(str(e))
    except User.DoesNotExist as e:
        raise ValueError(str(e))
    except Exception as e:
        raise ValueError(str(e))


def get_text_from_document(document):
    text = ""
    for page in document.pages.all():
        for element in page.parsed_data['elements']:
            if "text" in element:
                text += element['text'] + "\n"
    return text


@shared_task(bind=True)
def search_openai_for_docs(self, project_id, user_id, prompt, role_description):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting OpenAI Search...'})

    project, user, number_of_documents = get_project_and_user(project_id, user_id)
    client = AiApiClient(api='openai',
                         api_key=project.openai_api_key,
                         gpt_role_description=role_description)

    for document in project.documents.all():
        # Perform OpenAI search for each document
        context = get_text_from_document(document)
        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model=project.openai_model,
                                               prompt=prompt)
        document.metadata['openai_response'] = response
        document.save(current_user=user)

        # Update the progress
        percentage_complete = (document.id / number_of_documents) * 100
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': f'OpenAI Search in progress for document {document.id}...'})

    percentage_complete = 100

    self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                             'text': 'OpenAI Search Completed.'})


@shared_task(bind=True)
def search_gemini_for_docs(self, project_id, user_id, prompt, role_description):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Gemini Search...'})

    project, user, number_of_documents = get_project_and_user(project_id, user_id)
    client = AiApiClient(api='gemini',
                         api_key=project.gemini_api_key,
                         gpt_role_description=role_description)

    for document in project.documents.all():
        # Perform OpenAI search for each document
        context = get_text_from_document(document)

        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model=project.openai_model,
                                               prompt=prompt)
        document.metadata['gemini_response'] = response
        document.save(current_user=user)

        # Update the progress
        percentage_complete = (document.id / number_of_documents) * 100
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': f'OpenAI Search in progress for document {document.id}...'})

    percentage_complete = 100

    self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                             'text': 'OpenAI Search Completed.'})


@shared_task(bind=True)
def search_claude_for_docs(self, project_id, user_id, prompt, role_description):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting Claude Search...'})

    project, user, number_of_documents = get_project_and_user(project_id, user_id)
    client = AiApiClient(api='claude',
                         api_key=project.claude_api_key,
                         gpt_role_description=role_description)

    for document in project.documents.all():
        # Perform OpenAI search for each document
        context = get_text_from_document(document)

        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model=project.openai_model,
                                               prompt=prompt)
        document.metadata['claude_response'] = response
        document.save(current_user=user)

        # Update the progress
        percentage_complete = (document.id / number_of_documents) * 100
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': f'OpenAI Search in progress for document {document.id}...'})

    percentage_complete = 100

    self.update_state(state='SUCCESS', meta={'current': percentage_complete, 'total': 100,
                                             'text': 'OpenAI Search Completed.'})