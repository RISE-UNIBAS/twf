from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div, Button
from django import forms

from twf.models import Prompt, Page


class BaseBatchForm(forms.Form):
    """ Base form for batches of dictionaries. """

    project = None
    task_data = {}
    progress_details = forms.CharField(label='Progress', required=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)

        self.task_data['data-start-url'] = kwargs.pop('data-start-url', None)
        self.task_data['data-message'] = kwargs.pop('data-message', 'Are you sure you want to start the task?')
        self.task_data['data-progress-url-base'] = kwargs.pop('data-progress-url-base', "/celery/status/")
        self.task_data['data-progress-bar-id'] = kwargs.pop('data-progress-bar-id', "#taskProgressBar")
        self.task_data['data-log-textarea-id'] = kwargs.pop('data-log-textarea-id', "#id_progress_details")

        super().__init__(*args, **kwargs)

        if self.project is None:
            raise ValueError('Project must be provided.')

        progress_bar_html = """
        <div class="col-12 border text-center">
          <span>Progress:</span>
          <div class="progress">
            <div class="progress-bar bg-dark" role="progressbar" 
                 style="width: 0;" id="taskProgressBar" aria-valuenow="0" 
                 aria-valuemin="0" aria-valuemax="100">0%</div>
            </div>
        </div>"""

        self.fields['progress_details'].widget = forms.Textarea()
        self.fields['progress_details'].widget.attrs = {'readonly': True, 'rows': 5}

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        button_kwargs = {
            'css_class': 'btn btn-dark show-confirm-modal',
            'data_message': self.task_data.get('data-message'),
            'data_start_url': self.task_data.get('data-start-url'),
            'data_progress_url_base': self.task_data.get('data-progress-url-base'),
            'data_progress_bar_id': self.task_data.get('data-progress-bar-id'),
            'data_log_textarea_id': self.task_data.get('data-log-textarea-id'),
        }

        cancel_kwargs = {
            'css_class': 'btn btn-danger show-danger-modal',
            'data_message': 'Are you sure you want to cancel the task?',
            'disabled': 'disabled',
        }

        # Filter out None or empty values
        filtered_kwargs = {key: value for key, value in button_kwargs.items() if value}

        self.helper.layout = Layout(
            *self.get_dynamic_fields() or [],
            HTML(progress_bar_html),
            Row(
                Column('progress_details', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Button('cancelBatch', self.get_cancel_button_label(), **cancel_kwargs),
                Button('startBatch', self.get_button_label(), **filtered_kwargs),
                css_class='text-end pt-3'
            )
        )

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'

    def get_cancel_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class BaseAIBatchForm(BaseBatchForm):
    """ Base form for AI batches. """

    class Meta:
        js = ('twf/js/ai_prompt_manager.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['role_description'] = forms.CharField(label='Role Description', required=True)
        self.fields['prompt'] = forms.CharField(label='Prompt', required=True,
                                                widget=forms.Textarea(attrs={'rows': 5}))
        self.fields['saved_prompts'] = forms.ModelChoiceField(queryset=Prompt.objects.filter(project=self.project),
                                                              required=False)

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        button_html = """
         <div class="mt-4">
            <button type="button" id="loadPrompt" class="btn btn-sm btn-dark"
             data-bs-toggle="tooltip" title="Load the selected saved prompt. Unsaved edits are lost.">Load Prompt</button>
            <button type="button" id="savePrompt" class="btn btn-sm btn-dark"
             data-bs-toggle="tooltip" title="Overwrite selected prompt or save as new if no prompt selected.">Save Prompt</button>
        </div>"""

        fields = super().get_dynamic_fields() or []
        fields.append(
            Row(
                Column('role_description', css_class='form-group col-8 mb-0'),
                Column(HTML(button_html), css_class='form-group col-4 mb-0'),
                css_class='row form-row'
            )
        )
        fields.append(
            Row(
                Column('prompt', css_class='form-group col-8 mb-0'),
                Column('saved_prompts', css_class='form-group col-4 mb-0'),
                css_class='row form-row'
            )
        )
        return fields


class BaseMultiModalAIBatchForm(BaseAIBatchForm):
    """ Base form for AI batches with multimodal capabilities. """

    class Meta:
        js = ('twf/js/ai_prompt_manager.js',)

    # Mode choices for the prompt type
    PROMPT_MODE_CHOICES = [
        ('text_only', 'Text only'),
        ('images_only', 'Images only'),
        ('text_and_images', 'Text + Images')
    ]

    def __init__(self, *args, **kwargs):
        # Get the multimodal_support parameter and remove it from kwargs
        self.multimodal_support = kwargs.pop('multimodal_support', True)
        
        super().__init__(*args, **kwargs)
        
        if self.multimodal_support:
            # Add prompt mode selector
            self.fields['prompt_mode'] = forms.ChoiceField(
                label='Sending Mode',
                choices=self.PROMPT_MODE_CHOICES,
                initial='text_only',
                required=True,
                help_text='Select how to send the prompt to the AI model'
            )
            
            # Note: We no longer need a separate image_pages field since 
            # we'll automatically select up to 5 images per document

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form including multimodal fields if supported."""
        fields = super().get_dynamic_fields()
        
        if self.multimodal_support:
            # Add the mode selector
            fields.append(
                Row(
                    Column('prompt_mode', css_class='form-group col-12 mb-0'),
                    css_class='row form-row'
                )
            )
            
            # Add the fixed message about image limits
            image_info_html = """
            <div class="multimodal-info alert alert-info mt-2" style="display: none;">
                <small>
                    <i class="fas fa-info-circle"></i>
                    Up to 5 images per document will be included in the request (first 5 pages only).
                </small>
            </div>
            """
            
            fields.append(HTML(image_info_html))
            
            # Add JavaScript to show/hide the message based on mode selection
            modal_script = """
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const modeSelector = document.getElementById('id_prompt_mode');
                    const infoMessage = document.querySelector('.multimodal-info');
                    
                    function toggleInfoMessage() {
                        // Show message for any mode that includes images
                        const showMessage = modeSelector.value !== 'text_only';
                        infoMessage.style.display = showMessage ? 'block' : 'none';
                    }
                    
                    // Initial state
                    toggleInfoMessage();
                    
                    // Toggle on change
                    modeSelector.addEventListener('change', toggleInfoMessage);
                });
            </script>
            """
            
            fields.append(HTML(modal_script))
            
        return fields