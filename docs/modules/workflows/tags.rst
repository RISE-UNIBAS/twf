Tags
====

The **Tags** section in TWF provides tools to manage, extract, and normalize tags within your project.
These workflows streamline the process of handling tags and ensure consistency and organization across your datasets.

Tag Extraction
--------------

The **Tag Extraction** workflow allows users to extract tags from documents automatically. This is particularly
useful for generating tags based on text content, metadata, or other predefined criteria.

**Key Features:**

- Automated tag generation from document content.
- Supports customizable extraction criteria for different use cases.
- Allows bulk processing of documents.

**Workflow Steps:**

1. Navigate to **Tag Extraction > Extract Tags**.
2. Configure the extraction criteria or rules.
3. Start the extraction process.
4. Monitor progress in the **Task Monitor** or the extraction interface.
5. Review and refine the extracted tags in the **Tag Views** section.

**Example Use Case:**

- Extracting keywords or annotations from historical documents for categorization and retrieval.

---

Tag Workflows
-------------

The **Tag Workflows** section includes tools for organizing and normalizing tags within your project. These
workflows improve tag quality and ensure consistency across datasets.

### 1. Grouping Wizard

The **Grouping Wizard** is a semi-automated tool for grouping related tags together. It helps users merge similar
tags or organize them into meaningful categories.

**Key Features:**

- Identifies and suggests similar or duplicate tags.
- Allows manual adjustments and validation.
- Improves tag structure for easier navigation and retrieval.

**Workflow Steps:**

1. Go to **Tag Workflows > Grouping Wizard**.
2. Review the suggested tag groups.
3. Accept, reject, or manually adjust groupings.
4. Save the changes to update the tag organization.

**Example Use Case:**

- Merging similar tags like "WWII," "World War II," and "Second World War" into a single category.

---

### 2. Date Normalization

The **Date Normalization** workflow focuses on standardizing date-related tags in your project. It converts
ambiguous or inconsistent date formats into a unified format, ensuring better data quality.

**Key Features:**

- Supports various input formats, including full dates, partial dates, and ambiguous entries.
- Proposes normalized dates in the **EDTF (Extended Date/Time Format)** standard.
- Allows user validation and corrections.

**Workflow Steps:**

1. Open **Tag Workflows > Date Normalization**.
2. Select the date-related tags to normalize.
3. Review and adjust the proposed normalized dates.
4. Save the normalized tags.

**Example Use Case:**

- Converting tags like "2/11/23" and "November 2, 2023" into a consistent **2023-11-02** format.

---

Getting Started
---------------

1. Access the **Tags** section from the sidebar.
2. Choose between **Tag Extraction** or **Tag Workflows** depending on your task:
   - Use **Extract Tags** for automated tag generation.
   - Use **Grouping Wizard** or **Date Normalization** to organize and refine tags.
3. Follow the respective workflow steps and monitor progress in the **Task Monitor**.

Additional Notes
----------------

- The **Tag Views** section provides access to all tags categorized into:
  - **Open Tags**: Tags requiring further action.
  - **Parked Tags**: Tags temporarily set aside.
  - **Resolved Tags**: Tags that have been finalized.
  - **Ignored Tags**: Tags excluded from further processing.
- Tag workflows may require user input for validation
