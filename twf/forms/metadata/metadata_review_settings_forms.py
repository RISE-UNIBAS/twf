"""Forms for metadata review settings configuration."""

import json
import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, HTML
from django import forms
from django.utils.safestring import mark_safe

from twf.models import Document, Page

logger = logging.getLogger(__name__)


class MetadataReviewSettingsForm(forms.Form):
    """Form for configuring metadata review settings using table interface."""

    FIELD_TYPE_CHOICES = [
        ("text", "Text (single line)"),
        ("textarea", "Textarea (multi-line)"),
        ("number", "Number"),
        ("date", "Date"),
        ("select", "Select (dropdown)"),
    ]

    TARGET_CHOICES = [
        ("document", "Document Metadata"),
        ("page", "Page Metadata"),
    ]

    target_type = forms.ChoiceField(
        label="Review Target",
        choices=TARGET_CHOICES,
        initial="document",
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Choose whether to configure document or page metadata review",
    )

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not project:
            raise ValueError("Project is required for MetadataReviewSettingsForm")

        self.project = project

        # Get metadata keys for documents and pages
        doc_keys = Document.get_distinct_metadata_keys()
        page_keys = Page.get_distinct_metadata_keys()

        # Filter by project
        doc_key_counts = {}
        for key in doc_keys:
            count = Document.objects.filter(
                project=project, metadata__has_key=key
            ).count()
            if count > 0:
                doc_key_counts[key] = count

        page_key_counts = {}
        for key in page_keys:
            count = Page.objects.filter(
                document__project=project, metadata__has_key=key
            ).count()
            if count > 0:
                page_key_counts[key] = count

        # Load existing configuration
        conf_tasks = project.conf_tasks or {}
        metadata_config = conf_tasks.get("metadata_review", {})

        # Parse existing field configurations
        doc_field_config = {}
        page_field_config = {}

        if "document_field_config" in metadata_config:
            try:
                doc_field_config = json.loads(metadata_config["document_field_config"])
            except (json.JSONDecodeError, TypeError):
                pass

        if "page_field_config" in metadata_config:
            try:
                page_field_config = json.loads(metadata_config["page_field_config"])
            except (json.JSONDecodeError, TypeError):
                pass

        # Create fields for document metadata keys
        for metadata_key in sorted(doc_key_counts.keys()):
            count = doc_key_counts.get(metadata_key, 0)
            prefix = f"doc_{metadata_key.replace('.', '_')}"
            existing_config = doc_field_config.get(metadata_key, {})

            # Include checkbox
            self.fields[f"{prefix}_include"] = forms.BooleanField(
                label="",
                required=False,
                initial=existing_config.get("include", False),
                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
            )

            # Label field
            self.fields[f"{prefix}_label"] = forms.CharField(
                label="",
                required=False,
                initial=existing_config.get("label", ""),
                widget=forms.TextInput(
                    attrs={
                        "class": "form-control form-control-sm",
                        "placeholder": "Field label",
                    }
                ),
            )

            # Field type
            self.fields[f"{prefix}_type"] = forms.ChoiceField(
                label="",
                choices=self.FIELD_TYPE_CHOICES,
                initial=existing_config.get("type", "text"),
                widget=forms.Select(attrs={"class": "form-control form-control-sm"}),
            )

        # Create fields for page metadata keys
        for metadata_key in sorted(page_key_counts.keys()):
            count = page_key_counts.get(metadata_key, 0)
            prefix = f"page_{metadata_key.replace('.', '_')}"
            existing_config = page_field_config.get(metadata_key, {})

            # Include checkbox
            self.fields[f"{prefix}_include"] = forms.BooleanField(
                label="",
                required=False,
                initial=existing_config.get("include", False),
                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
            )

            # Label field
            self.fields[f"{prefix}_label"] = forms.CharField(
                label="",
                required=False,
                initial=existing_config.get("label", ""),
                widget=forms.TextInput(
                    attrs={
                        "class": "form-control form-control-sm",
                        "placeholder": "Field label",
                    }
                ),
            )

            # Field type
            self.fields[f"{prefix}_type"] = forms.ChoiceField(
                label="",
                choices=self.FIELD_TYPE_CHOICES,
                initial=existing_config.get("type", "text"),
                widget=forms.Select(attrs={"class": "form-control form-control-sm"}),
            )

        self.doc_keys = sorted(doc_key_counts.keys())
        self.doc_key_counts = doc_key_counts
        self.page_keys = sorted(page_key_counts.keys())
        self.page_key_counts = page_key_counts

        # Setup crispy forms helper
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "metadata-review-settings-form"
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3">Metadata Review Configuration</h4>'),
                HTML(
                    '<p class="text-muted">Configure which metadata fields to include in your review workflows.</p>'
                ),
                HTML(self._build_table_html()),
                Div(
                    Submit("submit", "Save Settings", css_class="btn btn-dark mt-3"),
                    css_class="mt-3",
                ),
                css_class="metadata-review-settings-container",
            )
        )

    def _build_table_html(self):
        """Build HTML tables for metadata field configuration."""
        html = """
        <div class="metadata-config-section mb-5">
            <h5 class="mb-3">
                <i class="fa fa-file-alt"></i> Document Metadata Fields
            </h5>
        """

        if self.doc_keys:
            html += """
            <div class="table-responsive">
                <table class="table table-hover table-sm">
                    <thead>
                        <tr>
                            <th style="width: 5%;">Include</th>
                            <th style="width: 30%;">Metadata Key</th>
                            <th style="width: 10%;">Count</th>
                            <th style="width: 30%;">Field Label</th>
                            <th style="width: 25%;">Field Type</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for metadata_key in self.doc_keys:
                count = self.doc_key_counts.get(metadata_key, 0)
                prefix = f"doc_{metadata_key.replace('.', '_')}"

                html += f"""
                    <tr>
                        <td class="text-center">
                            <div class="form-check">
                                {{{{ form.{prefix}_include }}}}
                            </div>
                        </td>
                        <td class="align-middle">
                            <code>{metadata_key}</code>
                        </td>
                        <td class="align-middle text-muted">{count}</td>
                        <td>{{{{ form.{prefix}_label }}}}</td>
                        <td>{{{{ form.{prefix}_type }}}}</td>
                    </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """
        else:
            html += """
            <div class="alert alert-info">
                <i class="fa fa-info-circle"></i> No document metadata found in this project.
            </div>
            """

        html += """
        </div>

        <div class="metadata-config-section">
            <h5 class="mb-3">
                <i class="fa fa-file"></i> Page Metadata Fields
            </h5>
        """

        if self.page_keys:
            html += """
            <div class="table-responsive">
                <table class="table table-hover table-sm">
                    <thead>
                        <tr>
                            <th style="width: 5%;">Include</th>
                            <th style="width: 30%;">Metadata Key</th>
                            <th style="width: 10%;">Count</th>
                            <th style="width: 30%;">Field Label</th>
                            <th style="width: 25%;">Field Type</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for metadata_key in self.page_keys:
                count = self.page_key_counts.get(metadata_key, 0)
                prefix = f"page_{metadata_key.replace('.', '_')}"

                html += f"""
                    <tr>
                        <td class="text-center">
                            <div class="form-check">
                                {{{{ form.{prefix}_include }}}}
                            </div>
                        </td>
                        <td class="align-middle">
                            <code>{metadata_key}</code>
                        </td>
                        <td class="align-middle text-muted">{count}</td>
                        <td>{{{{ form.{prefix}_label }}}}</td>
                        <td>{{{{ form.{prefix}_type }}}}</td>
                    </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """
        else:
            html += """
            <div class="alert alert-info">
                <i class="fa fa-info-circle"></i> No page metadata found in this project.
            </div>
            """

        html += """
        </div>
        """

        return mark_safe(html)

    def save(self):
        """Save the form data to the project configuration."""
        if not self.is_valid():
            return False

        # Build configuration dictionaries for documents
        doc_field_config = {}
        for metadata_key in self.doc_keys:
            prefix = f"doc_{metadata_key.replace('.', '_')}"

            include = self.cleaned_data.get(f"{prefix}_include", False)
            label = self.cleaned_data.get(f"{prefix}_label", "").strip()
            field_type = self.cleaned_data.get(f"{prefix}_type", "text")

            if include:
                doc_field_config[metadata_key] = {
                    "include": True,
                    "label": label or metadata_key,
                    "type": field_type,
                }

        # Build configuration dictionaries for pages
        page_field_config = {}
        for metadata_key in self.page_keys:
            prefix = f"page_{metadata_key.replace('.', '_')}"

            include = self.cleaned_data.get(f"{prefix}_include", False)
            label = self.cleaned_data.get(f"{prefix}_label", "").strip()
            field_type = self.cleaned_data.get(f"{prefix}_type", "text")

            if include:
                page_field_config[metadata_key] = {
                    "include": True,
                    "label": label or metadata_key,
                    "type": field_type,
                }

        # Update project configuration
        if not self.project.conf_tasks:
            self.project.conf_tasks = {}

        if "metadata_review" not in self.project.conf_tasks:
            self.project.conf_tasks["metadata_review"] = {}

        # Store as JSON strings
        self.project.conf_tasks["metadata_review"]["document_field_config"] = (
            json.dumps(doc_field_config, indent=2) if doc_field_config else ""
        )

        self.project.conf_tasks["metadata_review"]["page_field_config"] = (
            json.dumps(page_field_config, indent=2) if page_field_config else ""
        )

        # Keep legacy configurations for backward compatibility if they exist
        # (they will be replaced by the new config over time)

        self.project.save()
        logger.info(f"Metadata review settings saved for project {self.project.id}")

        return True
