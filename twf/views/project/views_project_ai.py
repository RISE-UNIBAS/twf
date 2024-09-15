import logging

from django.http import JsonResponse

from django.contrib import messages
from django.shortcuts import render
from django.views.generic import FormView

from twf.forms.project_forms import AIQueryDatabaseForm, BatchOpenAIForm
from twf.clients.simple_ai_clients import AiApiClient
from twf.views.project.views_project import TWFProjectView
from twf.tasks.openai_tasks import ask_chatgpt_task

logger = logging.getLogger(__name__)


class TWFProjectAIQueryView(FormView, TWFProjectView):
    template_name = 'twf/project/ai_query.html'
    page_title = 'AI Query'
    form_class = AIQueryDatabaseForm
    results = None

    def form_valid(self, form):
        # Save the form
        project = self.get_project()
        question = form.cleaned_data['question']
        gpt_role_description = "A Swiss History professor"
        model = "gpt-4-turbo"
        documents = form.cleaned_data['documents']
        context = ""
        for doc in documents:
            for page in doc.pages.all():
                for element in page.parsed_data['elements']:
                    if "text" in element:
                        context += element['text'] + "\n"

        client = AiApiClient(api='openai',
                             api_key=project.openai_api_key,
                             gpt_role_description=gpt_role_description)
        prompt = question + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model=model,
                                               prompt=prompt)

        # Add a success message
        messages.success(self.request, f'Answer received. Retrieving the answer took {elapsed_time:.2f} seconds.')

        # Redirect to the same URL
        context = self.get_context_data()
        context['result'] = response.choices[0].message.content
        context['form'] = form
        return render(self.request, self.template_name, context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add your custom argument here
        kwargs['project'] = self.get_project()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFProjectAIBatchView(FormView, TWFProjectView):
    template_name = 'twf/project/ai_batch_query.html'
    page_title = 'AI Query'
    form_class = BatchOpenAIForm
    results = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add your custom argument here
        kwargs['project'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        project = self.get_project()

        # Ensure form is valid before processing
        if form.is_valid():
            selection = form.cleaned_data['selection']
            role_description = form.cleaned_data['role_description']
            prompt = form.cleaned_data['prompt']

            # Correct project.id instead of project.d
            task = ask_chatgpt_task.delay(project.id, selection, role_description, prompt)

            return JsonResponse({'status': 'success', 'task_id': task.id})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def form_invalid(self, form):
        # If form is invalid, return an error response
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
