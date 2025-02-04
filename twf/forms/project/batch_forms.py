from twf.forms.base_batch_forms import BaseBatchForm


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