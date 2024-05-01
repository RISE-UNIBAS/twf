"""This module contains the models for the main app."""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from fuzzywuzzy import process


class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating 'created' and 'modified' fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    """The date and time the object was created."""

    modified_at = models.DateTimeField(auto_now=True)
    """The date and time the object was last modified."""

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='created_%(class)s_set', on_delete=models.CASCADE)
    """The user who created the object."""

    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='modified_%(class)s_set', on_delete=models.CASCADE)
    """The user who last modified the object."""

    class Meta:
        """Meta options for the TimeStampedModel."""
        abstract = True

    def save(self, *args, **kwargs):
        """Save the object."""
        user = kwargs.pop('current_user', None)
        if user is not None:
            if not self.pk:  # Check if this is a new object
                self.created_by = user
            self.modified_by = user
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """A user profile."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    """The user this profile belongs to."""

    clearance_level = models.IntegerField(default=0)  # You can define levels as constants
    """The clearance level of the user."""

    def get_projects(self):
        """Return the projects the user is a member of."""

        owned_projects = Project.objects.filter(owner=self, status='open')
        member_projects = Project.objects.filter(members=self, status='open')
        all_projects = owned_projects | member_projects
        all_projects = all_projects.distinct().order_by('id')
        return all_projects

    def __str__(self):
        """Return the string representation of the UserProfile."""
        return self.user.username


class Project(TimeStampedModel):
    """A project."""

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )
    """The choices for the status of the project."""

    title = models.CharField(max_length=100)
    """The title of the project."""

    collection_id = models.CharField(max_length=30)
    """The Transkribus collection ID."""

    transkribus_job_id = models.CharField(max_length=30, blank=True, null=True)
    """The Transkribus job ID of the last requested export."""

    job_download_url = models.URLField(blank=True, null=True)
    """The download URL of the last requested export."""

    downloaded_at = models.DateTimeField(blank=True, null=True)
    """The time the last export was downloaded."""

    downloaded_zip_file = models.FileField(upload_to='transkribus_exports/', blank=True, null=True)
    """The last downloaded export file."""

    metadata_google_sheet_id = models.CharField(max_length=100, blank=True, null=True,
                                                help_text='The ID of the Google Sheet containing metadata')
    """The ID of the Google Sheet containing metadata."""

    metadata_google_sheet_range = models.CharField(max_length=100, blank=True, null=True,
                                                   help_text='The range of the Google Sheet containing metadata')
    """The range of the Google Sheet containing metadata."""

    metadata_google_doc_id_column = models.CharField(max_length=50, blank=True, null=True,
                                                     help_text='The name of the column containing the document IDs')
    """The name of the column containing the document IDs."""

    metadata_google_title_column = models.CharField(max_length=50, blank=True, null=True,
                                                    help_text='The name of the column containing the document titles')
    """The name of the column containing the document titles."""

    metadata_google_valid_columns = models.CharField(max_length=512, blank=True, null=True,
                                                     help_text='A coma-separated list of valid column names '
                                                               'for metadata. Leave blank for all columns.')
    """A coma-separated list of valid column names for metadata. Leave blank for all columns."""

    description = models.TextField(blank=True, default='')
    """The description of the project."""

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    """The status of the project."""

    owner = models.ForeignKey(UserProfile, related_name='owned_projects', on_delete=models.CASCADE)
    """The owner of the project."""

    members = models.ManyToManyField(UserProfile, related_name='projects')
    """The members of the project."""

    tag_type_translator = models.JSONField(default=dict)
    """A dictionary to translate tag types."""

    ignored_tag_types = models.JSONField(default=dict)
    """A list of tag types to ignore."""

    def get_valid_cols(self):
        """Return the valid columns for metadata."""
        if self.metadata_google_valid_columns:
            return self.metadata_google_valid_columns.split(',')
        return []

    def get_transkribus_url(self):
        """Return the URL to the Transkribus collection."""
        return f"https://app.transkribus.org/collection/{self.collection_id}"

    def __str__(self):
        """Return the string representation of the Project."""
        return self.title


class Document(TimeStampedModel):
    """A document in a project."""

    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)
    """The project this document belongs to."""

    title = models.CharField(max_length=512, blank=True, default='')
    """The title of the document."""

    document_id = models.CharField(max_length=30)
    """The Transkribus document ID."""

    metadata = models.JSONField(default=dict)
    """Metadata for the document."""

    last_parsed_at = models.DateTimeField(null=True, blank=True)
    """The last time the document was parsed."""

    class Meta:
        """Meta options for the Document model."""
        ordering = ['document_id']

    def get_transkribus_url(self):
        """Return the URL to the Transkribus document."""
        return f"https://app.transkribus.org/collection/{self.project.collection_id}/doc/{self.document_id}"

    def __str__(self):
        """Return the string representation of the Document."""
        return f"Document for {self.project.title}"


def page_directory_path(instance, filename):
    """Gets the project name, processes it into a slug (a URL-friendly format without spaces or special characters)"""
    collection_id = instance.document.project.collection_id
    return f'transkribus_exports/{collection_id}/{filename}'


class Page(TimeStampedModel):
    """A page of a document."""

    document = models.ForeignKey(Document, related_name='pages', on_delete=models.CASCADE)
    """The document this page belongs to."""

    metadata = models.JSONField(default=dict)
    """Metadata for the page."""

    xml_file = models.FileField(upload_to=page_directory_path, null=False, blank=False)
    """The XML file of the page."""

    tk_page_id = models.CharField(max_length=30)
    """The Transkribus page ID."""

    tk_page_number = models.IntegerField(default=0)
    """The page number in the Transkribus document."""

    parsed_data = models.JSONField(default=dict)
    """The parsed data of the page."""

    num_tags = models.IntegerField(default=0)
    """The number of tags on the page."""

    is_ignored = models.BooleanField(default=False)
    """Whether the page is ignored."""

    class Meta:
        ordering = ['tk_page_number']

    def get_tags(self):
        tags = []
        for block in self.parsed_data['elements']:
            for tag in block['element_data']['custom_list_structure']:
                tags.append(tag)
        return tags

    def __str__(self):
        return f"Page {self.tk_page_number} of {self.document.document_id}"


class Dictionary(TimeStampedModel):
    """A dictionary."""

    label = models.CharField(max_length=100)
    """The label of the dictionary."""

    type = models.CharField(max_length=100)
    """The type of the dictionary."""

    class Meta:
        """Meta options for the Dictionary model."""
        ordering = ['label']

    def __str__(self):
        """Return the string representation of the Dictionary."""
        return self.label


class DictionaryEntry(TimeStampedModel):
    """An entry in a dictionary."""

    dictionary = models.ForeignKey(Dictionary, related_name='entries', on_delete=models.CASCADE)
    """The dictionary this entry belongs to."""

    label = models.CharField(max_length=255)
    """The label of the entry."""

    authorization_data = models.JSONField(default=dict)
    """Authorization data for the entry."""

    notes = models.TextField(blank=True, default='')
    """Notes for the entry."""

    class Meta:
        """Meta options for the DictionaryEntry model."""
        ordering = ['label']

    def get_documents(self):
        """Return the documents that contain this entry."""
        return Document.objects.filter(pages__tags__dictionary_entry=self).distinct()

    def get_num_usages(self):
        """Return the number of times this entry is used."""
        return PageTag.objects.filter(dictionary_entry=self).count()

    def __str__(self):
        """Return the string representation of the DictionaryEntry."""
        return self.label


class PageTag(TimeStampedModel):
    """A tag on a page."""

    page = models.ForeignKey(Page, related_name='tags', on_delete=models.CASCADE)
    """The page this tag belongs to."""

    variation = models.CharField(max_length=255)
    """The text of the tag."""

    variation_type = models.CharField(max_length=100)
    """The type of the tag."""

    dictionary_entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE,
                                         null=True, blank=True)
    """The dictionary entry this tag is assigned to."""

    additional_information = models.JSONField(default=dict)
    """Additional information about the tag."""

    normalized_variation = models.JSONField(default=dict)
    """The normalized version of the tag."""

    is_parked = models.BooleanField(default=False)
    """Whether the tag is parked."""

    class Meta:
        """Meta options for the PageTag model."""
        ordering = ['variation']

    def get_date(self):
        """Return the date in the format YYYY-MM-DD."""

        val = ""
        if "year" in self.additional_information:
            val = self.additional_information["year"]
        val += "-"
        if "month" in self.additional_information:
            val += f"{int(self.additional_information['month']):02}"
        val += "-"
        if "day" in self.additional_information:
            val += f"{int(self.additional_information['day']):02}"
        return val

    def get_transkribus_url(self):
        """Return the URL to the Transkribus page."""
        return (f"https://app.transkribus.org/collection/{self.page.document.project.collection_id}/doc/"
                f"{self.page.document.document_id}/detail/{self.page.tk_page_number}?view=combined")

    def assign_tag(self):
        """Assign the tag to a dictionary entry."""
        try:
            dictionary_type = self.variation_type
            if self.page.document.project.tag_type_translator.get(dictionary_type):
                dictionary_type = self.page.document.project.tag_type_translator[dictionary_type]
            entry = Variation.objects.get(variation=self.variation, entry__dictionary__type=dictionary_type)
            self.dictionary_entry = entry.entry
            self.save()
            return True
        except Variation.DoesNotExist:
            return False

    def get_closest_variations(self):
        """Return the 5 closest variations to the tag."""
        dict_type = self.variation_type
        if self.page.document.project.tag_type_translator.get(dict_type):
            dict_type = self.page.document.project.tag_type_translator[dict_type]

        variations = Variation.objects.filter(entry__dictionary__type=dict_type)
        variations_list = [variation.variation for variation in variations]

        # Using fuzzywuzzy to find the top 5 closest matches
        top_matches = process.extract(self.variation, variations_list, limit=5)

        # Retrieve the matched Variation objects
        closest_variations = []
        for match in top_matches:
            variation_text, score = match
            matched_variation = variations.filter(variation=variation_text).first()
            if matched_variation:
                closest_variations.append((matched_variation, score))

        return closest_variations

    def __str__(self):
        """Return the string representation of the PageTag."""
        return f"{self.variation_type}: {self.variation} ({self.page.document.project.title})"


class Variation(TimeStampedModel):
    """A variation of a dictionary entry."""

    entry = models.ForeignKey(DictionaryEntry, related_name='variations', on_delete=models.CASCADE)
    """The dictionary entry this variation belongs to."""

    variation = models.CharField(max_length=255)
    """The text of the variation."""

    class Meta:
        """Meta options for the Variation model."""
        ordering = ['variation']

    def __str__(self):
        """Return the string representation of the Variation."""
        return self.variation
