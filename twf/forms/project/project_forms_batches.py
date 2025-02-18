from crispy_forms.layout import Row, Column
from django import forms
from django_select2.forms import Select2MultipleWidget

from twf.forms.base_batch_forms import BaseBatchForm, BaseAIBatchForm
from twf.models import Document


class DocumentExtractionBatchForm(BaseBatchForm):
    """ Form for extracting documents from a Transkribus export. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Extract Documents From Transkribus Export'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class ProjectCopyBatchForm(BaseBatchForm):
    """ Form for copying a project. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Copy Project'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class ProjectAIBaseForm(BaseAIBatchForm):
    """Form for querying the AI model with a question and documents."""

    documents = forms.ModelMultipleChoiceField(label='Documents', required=True,
                                               help_text='Please select the documents to query.',
                                               widget=Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
                                               queryset=Document.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['documents'].queryset = Document.objects.filter(project=self.project)

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return super().get_dynamic_fields() + [
            Row(
                Column('documents', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
        ]



class OpenAIQueryDatabaseForm(ProjectAIBaseForm):

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Ask ChatGPT'


class GeminiQueryDatabaseForm(ProjectAIBaseForm):

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Ask Gemini'



class ClaudeQueryDatabaseForm(ProjectAIBaseForm):

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Ask Claude'
