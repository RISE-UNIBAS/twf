Settings
========

The Transkribus Workflow (TWF) application has two main types of settings:

1. Django application settings (system-wide)
2. Project-specific settings (per project)

Django Application Settings
---------------------------

These are standard Django settings that configure the entire application and are located in ``transkribusWorkflow/settings.py``:

* **Database configuration**: PostgreSQL is the default database
* **Security settings**: SECRET_KEY, ALLOWED_HOSTS
* **Installed apps and middleware**
* **Static and media file handling**
* **Authentication and user management**
* **Celery configuration** for background tasks
* **Email settings**
* **Logging configuration**

These settings are typically configured during installation and deployment, and most users won't need to modify them directly.

Project-specific Settings
------------------------

These settings can be configured for each project in the application through the user interface. They're organized into five main categories:

General Settings
^^^^^^^^^^^^^^^

Basic project information:

* **Title**: The name of your project
* **Description**: Detailed information about your project
* **Owner**: The project owner
* **Members**: Project team members
* **Selected dictionaries**: Dictionaries assigned to this project

Credential Settings
^^^^^^^^^^^^^^^^^^

API keys and authentication for external services:

* **Transkribus**: Username and password for Transkribus
* **OpenAI**: API key and default model
* **Google GenAI**: API key and default model
* **Anthropic**: API key and default model
* **Mistral**: API key and default model
* **Geonames**: Username
* **Zenodo**: API token for publishing

Task Settings
^^^^^^^^^^^^

Configuration for various automation tasks:

* **Google Sheets Integration**:
    * Sheet ID
    * Range
    * Valid columns
    * Document ID column
    * Document title column

* **Metadata Review**:
    * Page metadata review settings
    * Document metadata review settings

* **Date Normalization**:
    * Date input format (auto, DMY, YMD)
    * Date resolution precision

* **Tag Types**:
    * Tag type translator (JSON mapping)
    * Ignored tag types

Export Settings
^^^^^^^^^^^^^^

Configure how data is exported from the system:

* **Project Export Configuration**: Settings for exporting entire projects
* **Document Export Configuration**: Settings for document-level exports
* **Page Export Configuration**: Settings for page-level exports

Repository Settings
^^^^^^^^^^^^^^^^^^

Metadata for publishing and sharing:

* **Keywords**: Project keywords for discoverability
* **License**: Default is "CC BY 4.0"
* **Version**: Project version number
* **Workflow Description**: Markdown description of the project workflow
* **Project DOI**: Digital Object Identifier for the project

Accessing Settings
------------------

Project settings can be accessed and modified through the project settings interface:

1. Navigate to the project view
2. Click on "Settings" in the navigation menu
3. Choose the appropriate settings tab (General, Credentials, Tasks, Export, or Repository)
4. Modify the settings as needed
5. Click "Save" to apply your changes

Settings are stored in the database and associated with your specific project, allowing different projects to have different configurations.