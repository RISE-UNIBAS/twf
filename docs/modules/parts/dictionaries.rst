Dictionaries
============

The **Dictionaries** section enables users to manage structured entries that can be referenced across the
project for consistency and categorization. Dictionary entries are organized by type and can include
multiple variations, often derived from tags through the grouping wizard. Entries may also be enriched
with external references, such as GND or Geonames data, for standardized and validated identifiers.

Sections
--------

Dictionaries Options
^^^^^^^^^^^^^^^^^^^^

- **Overview**: Provides a summary of the dictionaries in use, showing the total count of dictionaries,
  the most referenced category, and the most frequently used entry. This high-level view helps users quickly
  gauge the dictionary's usage across the project.

- **Dictionaries**: Displays a list of all dictionaries and their entries, allowing users to manage and
  edit individual entries within each dictionary.

- **Create New Dictionary**: Allows users to create a new dictionary entry type, providing a structured
  system for grouping and categorizing tags or terms within the project.

- **Norm Data Wizard**: Facilitates the normalization of dictionary entries, helping to standardize entries
  and reduce variation in terminology across the dataset.

Automated Workflows
^^^^^^^^^^^^^^^^^^^
Automated workflows integrate with external data sources to enrich dictionary entries with validated
information, allowing for consistent referencing. These workflows operate independently and update entries
automatically:

- **GND**: Uses the Integrated Authority File (GND) to standardize dictionary entries with authoritative
  identifiers for people, places, and organizations.

- **Wikidata**: Integrates with Wikidata to pull additional metadata for dictionary entries, allowing users
  to enrich entries with structured data.

- **Geonames**: Links dictionary entries to geographic identifiers in the Geonames database, providing
  standardized location data.

- **Open AI**: Utilizes AI models to enrich entries with additional contextual information, such as category
  labels or semantic connections.

Supervised Workflows
^^^^^^^^^^^^^^^^^^^^
Supervised workflows allow users to review and validate automated updates, providing greater control over
dictionary entry enrichment. Users can confirm or modify external data suggestions before they are applied:

- **GND**: Allows users to review and confirm GND-sourced data before updating entries.
- **Wikidata**: Provides a validation step for data pulled from Wikidata.
- **Geonames**: Enables users to verify geographic data from Geonames.
- **Open AI**: Allows supervised review of AI-suggested enrichments or categorizations.

Dictionaries Overview
---------------------

**Dictionaries Overview** provides summary statistics and information, including:

- **Total Dictionaries**: The total number of dictionaries in the project.
- **Mostly Referenced Category**: The category most frequently referenced across dictionary entries.
- **Mostly Referenced Entry**: The individual entry most frequently referenced, which can indicate
  important entities or terms within the dataset.

Dictionary Entries by Type
--------------------------

This section displays a breakdown of dictionary entries by type, such as **health** and **location**, along
with usage statistics. Each entry shows the following:

- **Term**: The dictionary entry name, e.g., "Arzt," "Hamburg."
- **Used # Times**: Indicates the number of times each term has been used in the project, helping users
  understand the prominence of terms within each type.

Accompanying charts for each type (e.g., Health, Location) visually represent the frequency of dictionary
entries, giving users a quick view of distribution patterns within dictionary categories. This visual
feedback aids in identifying prominent terms and ensures balanced representation across categories.
