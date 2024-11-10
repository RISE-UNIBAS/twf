Project
=======

The **Project** section provides an overview of the current research project in TWF. It allows users to
configure core project settings, monitor ongoing tasks, and manage saved prompts.

Sections
--------

Overview
^^^^^^^^
Displays a summary of the selected project, including the project name, description, creator, creation date,
and the last modified timestamp. Key statistics are shown as well, such as the total number of documents,
pages, and users associated with the project.

Task Monitor
^^^^^^^^^^^^
The **Task Monitor** provides real-time updates on background tasks associated with the project. It allows
users to track the progress of tasks, such as document processing or metadata extraction, which might take
considerable time.

Saved Prompts
^^^^^^^^^^^^^
The **Saved Prompts** section lets users save commonly used prompts for easy access. These prompts can be
customized and reused across different parts of the project, enhancing workflow efficiency.

Settings
--------

General Settings
^^^^^^^^^^^^^^^^
Configures core settings specific to the project. This may include project-specific metadata fields,
visibility options, or general configurations that define the structure of the project.

Credential Settings
^^^^^^^^^^^^^^^^^^^
Manages API credentials and authentication information necessary for connecting to external services,
such as Transkribus for OCR processing, AI models, or geographic databases. Credentials are stored securely
and can be used across multiple tasks.

Task Settings
^^^^^^^^^^^^^
Allows configuration of background tasks associated with the project, such as automated workflows, batch
processes, or other tasks that require periodic execution or specific settings.

Export Settings
^^^^^^^^^^^^^^^
Defines settings related to data export, such as the preferred export format, fields to include in export
files, and options for structuring exported metadata. This enables customization of the data output to suit
research or analysis needs.

Setup Project
-------------

Request Transkribus Export
^^^^^^^^^^^^^^^^^^^^^^^^^^
Initiates an export request to Transkribus, allowing users to extract OCR data or transcriptions from the
platform directly into the TWF project.

Extract Transkribus Export
^^^^^^^^^^^^^^^^^^^^^^^^^^
Handles the extraction of data from a previously requested Transkribus export. This step completes the import
of OCR data or transcriptions, making it available for analysis and tagging within the project.

Ask Questions
-------------

Query
^^^^^
Allows users to formulate specific queries related to the project's data. This tool can be used to retrieve
targeted information or insights from the dataset, supporting various research questions.

Ask ChatGPT
^^^^^^^^^^^
Enables users to interact with ChatGPT directly from the interface, asking questions or requesting insights
related to the project data or metadata. This feature leverages language model capabilities for enhanced data
interpretation and support.

Data Counts
-----------

The **Data Counts** section provides an overview of statistical information for the project. Typical
statistics include:

- **Document Count**: Total number of documents within the project.
- **Page Count**: Total number of pages across all documents.
- **Average pages per document**: The average number of pages per document, offering insights into document
  structure and content density.
