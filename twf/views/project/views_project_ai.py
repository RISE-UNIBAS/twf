""" Views for the AI model. """
import logging

from django.contrib import messages
from django.shortcuts import render
from django.views.generic import FormView

from twf.forms.project.project_forms import AIQueryDatabaseForm
from twf.clients.simple_ai_clients import AiApiClient
from twf.views.project.views_project import TWFProjectView

logger = logging.getLogger(__name__)


class TWFProjectAIQueryView(FormView, TWFProjectView):
    """View for querying the AI model."""

    template_name = 'twf/project/questions/ai_query.html'
    page_title = 'AI Query'
    form_class = AIQueryDatabaseForm
    results = None

    def form_valid(self, form):
        # Save the form
        project = self.get_project()
        openai_credentials = project.get_credentials('openai')
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
                             api_key=openai_credentials.api_key,
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
