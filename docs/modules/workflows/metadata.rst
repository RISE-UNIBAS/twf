Metadata
========

Metadata in TWF refers to additional data associated with documents, pages, or projects. This layer of
information enriches the core documents by adding context or linking external data, such as ChatGPT responses
or dictionary-authorized data. Metadata can be imported from external sources or generated and reviewed using
workflows provided in the system.

Metadata Overview
-----------------

The **Metadata Overview** section provides insights into the metadata status of your project. Key statistics include:

- **Documents with Metadata**: The total number of documents enriched with metadata.
- **Pages with Metadata**: The total number of pages containing associated metadata.

**Example Use Cases:**

- Enriching historical documents with annotations or contextual information.
- Linking metadata extracted from external tools like Transkribus or PAGE.XML.

---

Load Metadata
-------------

The **Load Metadata** section allows users to import metadata into TWF from external sources, such as JSON files or
Google Sheets.

### Load JSON Metadata

This workflow supports importing metadata stored in JSON format. JSON is widely used for storing structured data
and is ideal for integration with other systems.

**Key Features:**

- Supports bulk import of metadata from JSON files.
- Allows mapping metadata fields to corresponding documents or pages.

**Workflow Steps:**

1. Navigate to **Load Metadata > Load JSON Metadata**.
2. Upload the JSON file containing metadata.
3. Map the fields in the JSON to the corresponding TWF data structure.
4. Confirm and initiate the import process.

**Example Use Case:**

- Importing metadata for a set of documents exported from another system.

---

### Load Google Sheets Metadata

This workflow supports importing metadata directly from Google Sheets. This is useful for collaborative metadata
management.

**Key Features:**

- Fetch metadata from Google Sheets via its API.
- Supports column mapping for flexible integration with existing metadata structures.

**Workflow Steps:**

1. Open **Load Metadata > Load Google Sheets Metadata**.
2. Provide the link to the Google Sheet and ensure proper sharing permissions are set.
3. Map the columns in the sheet to metadata fields in TWF.
4. Start the import process.

**Example Use Case:**

- Enriching project documents with metadata collaboratively curated in Google Sheets.

---

Metadata Workflows
------------------

The **Metadata Workflows** section includes tools for extracting, reviewing, and managing metadata within TWF.
These workflows ensure the quality and consistency of metadata across your project.

### 1. Extract Controlled Values

The **Extract Controlled Values** workflow identifies and extracts controlled values from metadata. Controlled
values are predefined values that ensure consistency and standardization in metadata fields.

**Key Features:**

- Extracts structured, controlled metadata values.
- Provides options to review and validate extracted values.

**Workflow Steps:**

1. Navigate to **Metadata Workflows > Extract Controlled Values**.
2. Select the metadata fields for extraction.
3. Review and approve the extracted values.

**Example Use Case:**

- Extracting standardized geographical names or author names from metadata.

---

### 2. Review Document Metadata

The **Review Document Metadata** workflow allows users to review, edit, and validate metadata associated with
documents.

**Key Features:**

- Displays metadata for each document.
- Allows inline editing for quick updates.
- Highlights discrepancies or missing metadata fields.

**Workflow Steps:**

1. Open **Metadata Workflows > Review Document Metadata**.
2. Review the metadata displayed for each document.
3. Make changes or corrections as necessary.
4. Save and confirm the updates.

**Example Use Case:**

- Ensuring all documents in a collection have consistent metadata fields.

---

### 3. Review Page Metadata

The **Review Page Metadata** workflow focuses on metadata associated with individual pages, providing a d
