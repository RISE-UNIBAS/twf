Documents
=========

The **Documents** section allows users to browse, search, and manage all documents within the project.
Documents are a fundamental unit within TWF, typically imported during project setup. Each document consists
of individual pages, enabling detailed exploration and metadata tagging. While documents can be created
manually, it is generally recommended to use batch import methods for efficiency.

Sections
--------

Your Documents
^^^^^^^^^^^^^^
- **Overview**: Displays a summary of the project's documents, including the total document count, the average
  number of pages per document, and the count and percentage of ignored documents.

- **Browse Documents**: Provides a list view of all documents in the project, allowing users to search and
  filter documents based on specific criteria or metadata fields.

Document Batch
^^^^^^^^^^^^^^
Allows users to process documents in batches using different AI services or tools. For example:

- **ChatGPT**: Process documents with ChatGPT, enabling automated insights, summaries, or other tasks.

- **Gemini**: Process documents with Gemini for specific analysis or metadata extraction.

- **Claude**: Use Claude for document processing tasks, supporting a range of document-based queries and
  transformations.

Create Documents
----------------
Provides options for creating new documents within the project. This includes:

- **Manual Document Creation**: Allows users to manually add documents when automated import is not feasible
  or if specific details are needed for each document.

Data Overview
-------------

**Documents Overview**: This section displays high-level statistics on the project's documents, including:

- **Document Count**: Total number of documents within the project.
- **Average number of pages**: The mean number of pages per document, which helps assess document structure.
- **Ignored Documents**: Number and percentage of documents marked as ignored, often used for documents that
  don't require further processing.

Metadata
--------

**Present Metadata Keys in Document Metadata**: Shows the metadata keys currently in use across documents.
These metadata fields, such as `claude_response`, `gemini_response`, and `openai_response`, represent data
attributes and responses from integrated AI tools. This section provides an overview of available metadata
for easier document management and retrieval.

