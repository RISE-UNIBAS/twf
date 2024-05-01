Creating a New Project
======================

Projects in the TWF system are created by administrators in the Django administration interface.
The web service frontend does not allow for the creation of projects.

Project Model
-------------

The `Project` model in Django is used to represent a project in the TWF system.
Here is a brief description of its fields:

- `STATUS_CHOICES`: The choices for the status of the project. It can be either 'Open' or 'Closed'.
- `title`: The title of the project.
- `collection_id`: The Transkribus collection ID.
- `transkribus_job_id`: The Transkribus job ID of the last requested export.
- `job_download_url`: The download URL of the last requested export.
- `downloaded_at`: The time the last export was downloaded.
- `downloaded_zip_file`: The last downloaded export file.
- `metadata_google_sheet_id`: The ID of the Google Sheet containing metadata.
- `metadata_google_sheet_range`: The range of the Google Sheet containing metadata.
- `metadata_google_doc_id_column`: The name of the column containing the document IDs in the Google Sheet.
- `metadata_google_title_column`: The name of the column containing the document titles in the Google Sheet.
- `metadata_google_valid_columns`: A comma-separated list of valid column names for metadata. Leave blank for all columns.
- `description`: The description of the project.
- `status`: The status of the project. It can be either 'open' or 'closed'.
- `owner`: The owner of the project. It is a foreign key to the `UserProfile` model.
- `members`: The members of the project. It is a many-to-many field to the `UserProfile` model.
- `tag_type_translator`: A dictionary to translate tag types.
- `ignored_tag_types`: A list of tag types to ignore.

The `Project` model also includes several methods:

- `get_valid_cols()`: Returns the valid columns for metadata.
- `get_transkribus_url()`: Returns the URL to the Transkribus collection.
- `__str__()`: Returns the string representation of the Project, which is its title.