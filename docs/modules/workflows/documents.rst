Document Workflows
==================

The **Document Workflows** section in TWF enables users to process documents in bulk using AI-powered tools.
These workflows are designed to streamline operations like querying large sets of documents or applying AI models
for analysis.

Workflows Overview
------------------

The **Document Batch** section includes the following workflows:

1. **ChatGPT**
2. **Gemini**
3. **Claude**

Each workflow allows users to interact with a specific AI system to perform tasks such as generating responses,
enriching metadata, or querying document content.

### 1. ChatGPT

The "ChatGPT" workflow leverages OpenAI's ChatGPT model to analyze and process documents in bulk. This workflow
supports generating responses based on user-defined prompts and document content.

**Key Features:**

- Interacts with OpenAI's ChatGPT for natural language processing tasks.
- Allows batch processing of multiple documents simultaneously.
- Saves responses as metadata for further use.

**Workflow Steps:**

1. Navigate to **Document Batch > ChatGPT**.
2. Fill in the following fields:
   - **Role Description**: Provide a description for the AI system's role in interpreting the prompt.
   - **Prompt**: Enter the instructions for the AI system to follow.
3. Choose one of the following options:
   - **Test One Document**: Run the workflow on a single document for testing purposes.
   - **Run Project Batch**: Apply the workflow to all selected documents in the project.
4. Monitor the progress in the **Progress** section or the **Task Monitor**.

**Example Use Case:**

- Extract summaries, themes, or key points from a collection of historical documents.

---

### 2. Gemini

The "Gemini" workflow is designed for processing documents using another AI model. This tool enables advanced
analysis and processing of text in large document sets.

**Key Features:**

- Integrates with the Gemini AI model for customized document processing.
- Facilitates extraction of specific information based on defined prompts.

**Workflow Steps:**

1. Open **Document Batch > Gemini**.
2. Define the role and prompt as per the task requirements.
3. Select either **Test One Document** or **Run Project Batch** to execute the workflow.
4. Check progress and results in the **Task Monitor** or directly in the **Progress** section.

---

### 3. Claude

The "Claude" workflow connects to Anthropic’s Claude model to provide AI-driven insights and analysis for documents.

**Key Features:**

- Uses Claude for tasks like generating summaries or answering questions based on document content.
- Suitable for scenarios requiring a balance between AI reasoning and simplicity.

**Workflow Steps:**

1. Go to **Document Batch > Claude**.
2. Enter the **Role Description** and **Prompt** to guide the AI.
3. Run the workflow by choosing either **Test One Document** or **Run Project Batch**.
4. View the progress in the **Progress** section or in the **Task Monitor**.

---

Document Management
-------------------

TWF provides comprehensive tools for browsing and searching documents in your project. These features help you efficiently locate and manage your documents based on various criteria.

### Browse Documents

The **Browse Documents** view displays all documents in your project with filtering options. 

**Key Features:**
- View all documents in a tabular format
- Filter documents by status, type, and other attributes
- Access quick actions for each document

To access this view, navigate to **Documents > Browse Documents** in the sidebar navigation.

### Search Documents

The **Search Documents** view provides a powerful search interface to find specific documents across your project.

**Key Features:**
- Search documents by keyword across multiple fields
- Filter search results by document status
- Apply special filters like "Only Parked Documents," "Has Pages," or "Has Tags"
- Sort results by title, document ID, or date
- View detailed information about search results including tag counts and types

**Search Options:**
- **Search Term**: Enter keywords to search for in documents
- **Search Type**: Specify where to search (All Fields, Document Title, Document ID, etc.)
- **Document Status**: Filter by status (Open, Needs Work, Irrelevant, Reviewed)
- **Special Filters**: Apply additional filters for specific document attributes
- **Sort By**: Order results by various attributes

To perform a document search:
1. Navigate to **Documents > Search Documents** in the sidebar
2. Enter your search criteria in the form
3. Click "Search Documents" to view matching results
4. Use the results table to view and access the found documents

Getting Started
---------------

1. Access the **Document Batch** section in the sidebar navigation.
2. Choose the desired workflow (ChatGPT, Gemini, or Claude).
3. Define the workflow parameters, including the role description and prompt.
4. Execute the workflow and monitor the results.

Additional Notes
----------------

- Ensure that appropriate API credentials are configured in the **Project Settings** before starting the workflows.
- Batch operations may take time to complete. Tasks run in the background and can be tracked via the **Task Monitor**.
- Test individual documents before running batch operations to ensure prompt accuracy.
