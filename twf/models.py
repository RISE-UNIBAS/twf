"""This module contains the models for the twf app. The models are used to store data in the database.
Each module class represents a table in the database. The classes are subclasses of Django's models.Model class.

The main model is the Project model, which represents a project in the app. Most other models rely directly or
indirectly on the Project model. Most models extend the TimeStampedModel class, which provides self-updating
'created' and 'modified' fields. This means, every time an object is created or modified, the 'created_at' and
'modified_at' fields are updated automatically, but the user who created or modified the object must be provided.
"""
import json

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from twf.templatetags.tk_tags import tk_iiif_url, tk_bounding_box

# The User model is retrieved dynamically to allow for custom user models
User = get_user_model()

# The permission groups in the app (#TODO this is not implemented yet)
TWF_GROUPS = ['Setup Project', 'Group Tags', 'Run Batches', 'Import Dictionaries', 'Manipulate Dictionaries']


class TimeStampedModel(models.Model):
    """
    TimeStampedModel
    ----------------
    An abstract base class model that provides self-updating 'created' and 'modified' fields.
    Most models in the app extend this class to provide these fields.

    Attributes
    ~~~~~~~~~~
    created_at : DateTimeField
        The date and time the object was created.
    modified_at : DateTimeField
        The date and time the object was last modified.
    created_by : ForeignKey
        The user who created the object.
    modified_by : ForeignKey
        The user who last modified the object.
    """

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
    """
    User Profile Model
    ------------------
    User profiles are used to store additional information about users. This model extends the Django User model
    and provides additional fields to store user-specific data. The UserProfile model is linked to the User model
    via a OneToOneField, which means that each user can have only one profile.

    Attributes
    ~~~~~~~~~~
    user : OneToOneField
        The user this profile belongs to.
    clearance_level : IntegerField
        The clearance level of the user. This can be used to define different levels of access or permissions.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    """The user this profile belongs to."""

    clearance_level = models.IntegerField(default=0)  # You can define levels as constants
    """The clearance level of the user."""

    orc_id = models.CharField(max_length=255, blank=True, null=True)
    """The ORCID of the user."""

    affiliation = models.CharField(max_length=255, blank=True, null=True)
    """The affiliation of the user."""

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
    """
    Project Model
    -------------
    Projects are the main entities in the app. Each project represents a collection of documents and pages that
    are related to a specific task or topic. Projects can have multiple members, each with different roles and
    permissions. The Project model extends the TimeStampedModel, which provides self-updating 'created' and 'modified'
    fields.
    """

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )
    """The choices for the status of the project."""

    title = models.CharField(max_length=100,
                             verbose_name='Project Title',
                             help_text='The title of the project. Can be used in data exports.')
    """The title of the project."""

    collection_id = models.CharField(max_length=30,
                                     verbose_name='Transkribus Collection ID',
                                     help_text='The Transkribus collection ID. '
                                               'Needed to export your data from Transkribus.')
    """The Transkribus collection ID."""

    transkribus_job_id = models.CharField(max_length=30, blank=True, null=True,
                                          verbose_name='Transkribus Job ID',
                                          help_text='This value is set by the system and should only be changed '
                                                    'to manually point TWF to a finished export job.')
    """The Transkribus job ID of the last requested export."""

    job_download_url = models.URLField(blank=True, null=True,
                                       verbose_name='Transkribus Job Download URL',
                                       help_text='The download URL of the last requested export.'
                                                 'This value is set by the system and should only be changed '
                                                 'to manually point TWF to a finished export job.')
    """The download URL of the last requested export."""

    downloaded_at = models.DateTimeField(blank=True, null=True,
                                         verbose_name='Last Export Downloaded At',
                                         help_text='The time the last export was downloaded.')
    """The time the last export was downloaded."""

    downloaded_zip_file = models.FileField(upload_to='transkribus_exports/', blank=True, null=True,
                                           verbose_name='Last Export File',
                                           help_text='The last downloaded export file.')
    """The last downloaded export file."""

    description = models.TextField(blank=True, default='',
                                   verbose_name='Project Description',
                                   help_text='The description of the project. Should be brief. '
                                             'Can be used in data exports.')
    """The description of the project."""

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open',
                              verbose_name='Project Status',
                              help_text='The status of the project.')
    """The status of the project."""

    owner = models.ForeignKey(UserProfile, related_name='owned_projects', on_delete=models.CASCADE,
                              verbose_name='Project Owner')
    """The owner of the project."""

    members = models.ManyToManyField(UserProfile, related_name='projects',
                                     blank=True,
                                     verbose_name='Project Members',
                                     help_text='The members of the project. Their roles can be adjusted'
                                               'in the user management section.')
    """The members of the project."""

    selected_dictionaries = models.ManyToManyField('Dictionary', related_name='selected_projects',
                                                   blank=True, verbose_name='Selected Dictionaries',
                                                   help_text='The dictionaries selected for this project.')
    """The dictionaries selected for this project."""

    conf_credentials = models.JSONField(default=dict, blank=True,
                                        verbose_name='Credentials Configurations',
                                        help_text='A dictionary of credential configurations.')

    conf_export = models.JSONField(default=dict, blank=True,
                                   verbose_name='Export Configurations',
                                   help_text='A dictionary of export configurations.')

    conf_tasks = models.JSONField(default=dict, blank=True,
                                  verbose_name='Task Configurations',
                                  help_text='A dictionary of task configurations.')

    def get_credentials(self, service):
        """Return the credentials for a service.

        Available services
        ------------------

        """
        return self.conf_credentials.get(service, {})

    def get_export_configuration(self, service, return_json=True):
        """Return the export configuration for a service."""
        if return_json:
            value = self.conf_export.get(service, None)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return {}
            return {}
        return self.conf_export.get(service, '')


    def get_task_configuration(self, service, return_json=True):
        """Return the task configuration for a service.
        Available services
        ------------------
        - google_sheet: The Google Sheet configuration.
        - metadata_review: The metadata review configuration.
        - date_normalization: The date normalization configuration.
        - tag_types: The tag types configuration.
        """
        if return_json:
            value = self.conf_tasks.get(service, None)
            if value:
                if isinstance(value, dict):
                    return value
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return {}
            return {}
        return self.conf_tasks.get(service, {})

    def get_transkribus_url(self):
        """Return the URL to the Transkribus collection."""
        return f"https://app.transkribus.org/collection/{self.collection_id}"

    def __str__(self):
        """Return the string representation of the Project."""
        return self.title.__str__()


class Task(models.Model):
    """
    Task Model
    ----------
    Tasks are used to store Celery tasks in the database. This model is used to keep track of the status of tasks
    and to store additional information about the tasks. The Task model is linked to the Project model via a ForeignKey,
    which means that each task belongs to a specific project.

    Attributes
    ~~~~~~~~~~
    project : ForeignKey
        The project this task belongs to.
    user : ForeignKey
        The user who created the task.
    task_id : CharField
        The ID of the Celery task.
    status : CharField
        The status of the task.
    start_time : DateTimeField
        The time the task was started.
    end_time : DateTimeField
        The time the task was completed.
    title : CharField
        The title of the task.
    description : TextField
        The description of the task.
    text : TextField
        The text of the task.
    meta : JSONField
        Additional metadata for the task.
    """

    TASK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('STARTED', 'Started'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('PROGRESS', 'Progress'),
        ('CANCELLED', 'Cancelled'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    """The project this task belongs to."""

    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="tasks")
    """The user who created the task."""

    task_id = models.CharField(max_length=255, unique=True)
    """The ID of the Celery task."""

    status = models.CharField(max_length=10, choices=TASK_STATUS_CHOICES, default='PENDING')
    """The status of the task."""

    start_time = models.DateTimeField(default=timezone.now)
    """The time the task was started."""

    end_time = models.DateTimeField(null=True, blank=True)
    """The time the task was completed."""

    title = models.CharField(max_length=255, blank=True, default='')
    """The title of the task."""

    description = models.TextField(blank=True, default='')
    """The description of the task."""

    text = models.TextField(blank=True, default='')
    """The text of the task."""

    meta = models.JSONField(default=dict, blank=True)
    """Additional metadata for the task."""

    def __str__(self):
        return f"Task - {self.task_id} ({self.status})"


class Document(TimeStampedModel):
    """
    Document Model
    --------------
    Documents are used to store information about the documents in a project. Each document belongs to a specific
    project and can have multiple pages. The Document model extends the TimeStampedModel, which provides self-updating
    'created' and 'modified' fields.

    Attributes
    ~~~~~~~~~~
    project : ForeignKey
        The project this document belongs to.
    title : CharField
        The title of the document.
    document_id : CharField
        The Transkribus document ID.
    metadata : JSONField
        Metadata for the document.
    last_parsed_at : DateTimeField
        The last time the document was parsed.
    is_parked : BooleanField
        Whether the document is parked.
    workflow_remarks : TextField
        Workflow remarks for the document.
    """

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('needs_tk_work', 'Needs Correction on Transkribus'),
        ('irrelevant', 'Is Irrelevant'),
        ('reviewed', 'Reviewed'),
    ]

    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)
    """The project this document belongs to."""

    title = models.CharField(max_length=512, blank=True, default='')
    """The title of the document."""

    document_id = models.CharField(max_length=30)
    """The Transkribus document ID."""

    metadata = models.JSONField(default=dict, blank=True)
    """Metadata for the document."""

    last_parsed_at = models.DateTimeField(null=True, blank=True)
    """The last time the document was parsed."""

    is_parked = models.BooleanField(default=False, blank=True)
    """Whether the document is parked."""

    workflow_remarks = models.TextField(blank=True, default='')
    """Workflow remarks for the document."""

    is_reserved = models.BooleanField(default=False)
    """Whether the document is reserved for a workflow."""

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    class Meta:
        """Meta options for the Document model."""
        ordering = ['document_id']

    def get_transkribus_url(self):
        """Return the URL to the Transkribus document."""
        return f"https://app.transkribus.org/collection/{self.project.collection_id}/doc/{self.document_id}"

    def get_active_pages(self):
        """Return the active pages of the document."""
        return self.pages.filter(is_ignored=False)

    def __str__(self):
        """Return the string representation of the Document."""
        if self.title:
            return self.title

        return f"Document for {self.project.title}"


def page_directory_path(instance, filename):
    """Gets the project name, processes it into a slug (a URL-friendly format without spaces or special characters)"""
    collection_id = instance.document.project.collection_id
    return f'transkribus_exports/{collection_id}/{filename}'


class Page(TimeStampedModel):
    """
    Page Model
    ----------

    Pages are used to store information about the pages in a document. Each page belongs to a specific document and
    can have multiple tags. The Page model extends the TimeStampedModel, which provides self-updating 'created' and
    'modified' fields.

    Attributes
    ~~~~~~~~~~
    document : ForeignKey
        The document this page belongs to.
    metadata : JSONField
        Metadata for the page.
    xml_file : FileField
        The XML file of the page.
    tk_page_id : CharField
        The Transkribus page ID.
    tk_page_number : IntegerField
        The page number in the Transkribus document.
    parsed_data : JSONField
        The parsed data of the page.
    num_tags : IntegerField
        The number of tags on the page.
    is_ignored : BooleanField
        Whether the page is ignored.
    """

    document = models.ForeignKey(Document, related_name='pages', on_delete=models.CASCADE)
    """The document this page belongs to."""

    metadata = models.JSONField(default=dict, blank=True)
    """Metadata for the page."""

    xml_file = models.FileField(upload_to=page_directory_path, null=False, blank=False)
    """The XML file of the page."""

    tk_page_id = models.CharField(max_length=30)
    """The Transkribus page ID."""

    tk_page_number = models.IntegerField(default=0)
    """The page number in the Transkribus document."""

    parsed_data = models.JSONField(default=dict, blank=True)
    """The parsed data of the page."""

    num_tags = models.IntegerField(default=0)
    """The number of tags on the page."""

    is_ignored = models.BooleanField(default=False)
    """Whether the page is ignored."""

    class Meta:
        ordering = ['tk_page_number']

    def get_annotations(self):
        """Return the annotations of the page."""
        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        ret_items = []
        anno_types = []
        if 'elements' in self.parsed_data:
            # print("Elements found ({})".format(len(self.parsed_data['elements'])))
            for item in self.parsed_data['elements']:
                ret_item = {}
                element_data = item['element_data']
                el_type = None
                el_coords = None

                ret_item['text'] = "\n".join(element_data['text_lines'])

                if "structure" in element_data['custom_structure']:
                    el_type = element_data['custom_structure']['structure']['type']
                    ret_item['type'] = el_type
                if 'coords' in element_data:
                    el_coords = element_data['coords']

                try:
                    file_url = self.parsed_data['file']['imgUrl']
                    coords = tk_bounding_box(el_coords)
                    url = tk_iiif_url(file_url, coords=",".join([str(c) for c in coords]), image_size='pct:25')
                    ret_item['url'] = url
                except AttributeError:
                    ret_item['url'] = ''
                    # print("No file URL found")

                ret_item['id'] = element_data['id']

                ret_items.append(ret_item)
                anno_types.append(el_type)

        return ret_items

    def __str__(self):
        return f"Page {self.tk_page_number} of {self.document.document_id}"


class Dictionary(TimeStampedModel):
    """
    Dictionary Model
    ----------------
    Dictionaries are used to store dictionaries in the app. Each dictionary can have multiple entries. The Dictionary
    model extends the TimeStampedModel, which provides self-updating 'created' and 'modified' fields.

    Attributes
    ~~~~~~~~~~
    label : CharField
        The label of the dictionary. This should be unique and descriptive.
    type : CharField
        The type of the dictionary.
    """

    label = models.CharField(max_length=100, unique=True,
                             help_text='The label of the dictionary. This should be unique and descriptive.')
    """The label of the dictionary."""

    type = models.CharField(max_length=100,
                            help_text='The type of the dictionary. This means the Transkribus tag type.')
    """The type of the dictionary."""

    class Meta:
        """Meta options for the Dictionary model."""
        ordering = ['label']

    def __str__(self):
        """Return the string representation of the Dictionary."""
        return self.label.__str__()


class DictionaryEntry(TimeStampedModel):
    """
    DictionaryEntry Model
    ---------------------
    DictionaryEntries are used to store entries in a dictionary. Each entry belongs to a specific dictionary and can
    have additional information about the entry. The DictionaryEntry model extends the TimeStampedModel, which provides
    self-updating 'created' and 'modified' fields.

    Attributes
    ~~~~~~~~~~
    dictionary : ForeignKey
        The dictionary this entry belongs to.
    label : CharField
        The label of the entry.
    authorization_data : JSONField
        Authorization data for the entry.
    notes : TextField
        Notes for the entry.
    """

    dictionary = models.ForeignKey(Dictionary, related_name='entries', on_delete=models.CASCADE)
    """The dictionary this entry belongs to."""

    label = models.CharField(max_length=255)
    """The label of the entry."""

    authorization_data = models.JSONField(default=dict, blank=True)
    """Authorization data for the entry."""

    notes = models.TextField(blank=True, default='')
    """Notes for the entry."""

    is_reserved = models.BooleanField(default=False)
    """Whether the entry is reserved for a workflow."""

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
    """
    PageTag Model
    -------------

    PageTags are used to store tags on pages. Each PageTag belongs to a specific page and can have additional
    information about the tag. The PageTag model extends the TimeStampedModel, which provides self-updating 'created'
    and 'modified' fields.

    Attributes
    ~~~~~~~~~~
    page : ForeignKey
        The page this tag belongs to.
    variation : CharField
        The text of the tag.
    variation_type : CharField
        The type of the tag.
    dictionary_entry : ForeignKey
        The dictionary entry this tag is assigned to.
    additional_information : JSONField
        Additional information about the tag.
    date_variation_entry : ForeignKey
        The date variation entry.
    is_parked : BooleanField
        Whether the tag is parked.
    """

    page = models.ForeignKey(Page, related_name='tags', on_delete=models.CASCADE)
    """The page this tag belongs to."""

    variation = models.CharField(max_length=255)
    """The text of the tag."""

    variation_type = models.CharField(max_length=100)
    """The type of the tag."""

    dictionary_entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE,
                                         null=True, blank=True)
    """The dictionary entry this tag is assigned to."""

    additional_information = models.JSONField(default=dict, blank=True)
    """Additional information about the tag."""

    date_variation_entry = models.ForeignKey('DateVariation', on_delete=models.CASCADE,
                                             null=True, blank=True)

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

    def __str__(self):
        """Return the string representation of the PageTag."""
        return f"{self.variation_type}: {self.variation} ({self.page.document.project.title})"


class Variation(TimeStampedModel):
    """
    Variation Model
    ---------------
    Variations are used to store different variations of dictionary entries. This model is used to store variations
    of dictionary entries and to link them to the dictionary entries. The Variation model is linked to the
    DictionaryEntry model via a ForeignKey, which means that each variation belongs to a specific dictionary entry.

    Attributes
    ~~~~~~~~~~
    entry : ForeignKey
        The dictionary entry this variation belongs to.
    variation : CharField
        The text of the variation.
    """

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


class DateVariation(TimeStampedModel):
    """
    DateVariation Model
    -------------------

    DateVariations are used to store different variations of dates. This model is used to store variations of dates
    and to link them to the dictionary entries. The DateVariation model is linked to the DictionaryEntry model via a
    ForeignKey, which means that each date variation belongs to a specific dictionary entry.

    Attributes
    ~~~~~~~~~~
    entry : ForeignKey
        The dictionary entry this date variation belongs to.
    variation : CharField
        The text of the variation.
    normalized_variation : JSONField
        The normalized version of the variation.
    edt_of_normalized_variation : CharField
        The EDTF of the normalized variation.
    """

    variation = models.CharField(max_length=255)
    """The text of the variation."""

    normalized_variation = models.JSONField(default=dict, blank=True)
    """The normalized version of the variation."""

    edtf_of_normalized_variation = models.CharField(max_length=100)
    """The EDTF of the normalized variation."""

    class Meta:
        """Meta options for the Variation model."""
        ordering = ['variation']

    def __str__(self):
        """Return the string representation of the Variation."""
        return self.variation


class Collection(TimeStampedModel):
    """
    Collection Model
    ----------------
    Collections are (who would've thought) collections of documents or document parts.
    A collection belongs to a project and can be used to group its documents in a meaningful way.
    This model extends the TimeStampedModel, which provides self-updating 'created' and 'modified' fields.

    Attributes
    ~~~~~~~~~~
    project : ForeignKey
        The project this collection belongs to.
    title : CharField
        The title of the collection. This is descriptive and should be unique within the project.
    description : TextField
        The description of the collection

    """

    project = models.ForeignKey(Project, related_name='collections', on_delete=models.CASCADE)
    """The project this collection belongs to."""

    title = models.CharField(max_length=255)
    """The title of the collection. This is descriptive and should be unique within the project."""

    description = models.TextField(blank=True, default='')
    """The description of the collection."""

    def __str__(self):
        """Return the string representation of the Collection."""
        return self.title

    class Meta:
        """Meta options for the Collection model."""
        ordering = ['title']

class CollectionItem(TimeStampedModel):
    """
    CollectionItem Model
    --------------------

    CollectionItems are used to store items in a collection. Each CollectionItem belongs to a specific collection
    and can have additional information about the item. The CollectionItem model extends the TimeStampedModel, which
    provides self-updating 'created' and 'modified' fields.

    Attributes
    ~~~~~~~~~~
    collection : ForeignKey
        The collection this item belongs to.
    document : ForeignKey
        The document this item belongs to.
    document_configuration : JSONField
        The configuration of the document in the collection.
    title : CharField
        The title of the item.
    status : CharField
        The status of the item.
    review_notes : TextField
        Notes from the review of the item.
    """

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('reviewed', 'Reviewed'),
        ('faulty', 'Faulty'),
    )

    collection = models.ForeignKey(Collection, related_name='items', on_delete=models.CASCADE)
    """The collection this item belongs to."""

    document = models.ForeignKey(Document, related_name='collections', on_delete=models.CASCADE)
    """The document this item belongs to."""

    document_configuration = models.JSONField(default=dict, blank=True)
    """The configuration of the document in the collection."""

    title = models.CharField(max_length=255)
    """The title of the item."""

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    """The status of the item."""

    review_notes = models.TextField(blank=True, default='')
    """Notes from the review of the item."""

    is_reserved = models.BooleanField(default=False)
    """Whether the item is reserved for a workflow."""

    def __str__(self):
        """Return the string representation of the CollectionItem."""
        return f"{self.collection.title}: {self.title}"

    class Meta:
        """Meta options for the Collection model."""
        ordering = ['title']


class Prompt(TimeStampedModel):
    """
    Prompt Model
    ------------

    Prompts are used to store prompts for AI API requests. Each prompt can have additional information about the prompt.
    The Prompt model extends the TimeStampedModel, which provides self-updating 'created' and 'modified' fields.

    Attributes
    ~~~~~~~~~~
    project : ForeignKey
        The project this prompt belongs to.
    system_role : CharField
        The title of the prompt.
    prompt : TextField
        The prompt text.
    document_context : ManyToManyField
        The documents to include in the context
    page_context : ManyToManyField
        The pages to include in the context
    collection_context : ManyToManyField
        The collection items to include in the context
    """

    project = models.ForeignKey(Project, related_name='prompts', on_delete=models.CASCADE)
    """The project this prompt belongs to."""

    system_role = models.CharField(max_length=100)
    """The title of the prompt."""

    prompt = models.TextField()
    """The prompt text."""

    document_context = models.ManyToManyField(Document, related_name='prompts', blank=True)
    """The documents to include in the context"""

    page_context = models.ManyToManyField(Page, related_name='prompts', blank=True)
    """The pages to include in the context"""

    collection_context = models.ManyToManyField(CollectionItem, related_name='prompts', blank=True)
    """The collection items to include in the context"""

    def __str__(self):
        """Return the string representation of the Prompt."""
        return self.prompt[:50]


class Workflow(models.Model):
    """Model to store workflow information."""
    WORKFLOW_TYPE_CHOICES = [
        ('review_documents', 'Review Documents'),
        ('review_collection', 'Review Collection'),
        ('supervised_dictionary', 'Supervised Dictionary Workflow'),
    ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workflows")

    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=[('started', 'Started'), ('ended', 'Ended')], default='started')
    item_count = models.PositiveIntegerField()
    current_item_index = models.PositiveIntegerField(default=0)

    collection = models.ForeignKey('Collection', on_delete=models.SET_NULL, null=True, blank=True)
    dictionary = models.ForeignKey('Dictionary', on_delete=models.SET_NULL, null=True, blank=True)
    related_task = models.OneToOneField('Task', on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Newly added field to store assigned documents
    assigned_document_items = models.ManyToManyField('Document', related_name="workflows")
    assigned_dictionary_entries = models.ManyToManyField('DictionaryEntry', related_name="workflows")
    assigned_collection_items = models.ManyToManyField('CollectionItem', related_name="workflows")

    def get_next_item(self):
        """Fetch the next item to work on."""
        if self.workflow_type == 'review_documents':
            if self.current_item_index < self.item_count:
                item = self.assigned_document_items.all()[self.current_item_index]
                return item
        if self.workflow_type == 'review_collection':
            if self.current_item_index < self.item_count:
                item = self.assigned_collection_items.all()[self.current_item_index]
                return item

        return None

    def advance(self):
        """Advance the workflow to the next item."""
        self.current_item_index += 1
        self.save()

    def finish(self):
        """Mark the workflow as ended."""
        self.status = 'ended'
        self.save()

        # Update the related task status if linked
        if self.related_task:
            self.related_task.status = 'SUCCESS'
            self.related_task.end_time = timezone.now()
            self.related_task.save()

        # Restore the reserved status of the items
        if self.workflow_type == 'review_documents':
            for item in self.assigned_document_items.all():
                item.is_reserved = False
                item.save()
        if self.workflow_type == 'review_collection':
            for item in self.assigned_collection_items.all():
                item.is_reserved = False
                item.save()

    def has_more_items(self):
        """Check if there are more items to work on."""
        return self.current_item_index+1 < self.item_count