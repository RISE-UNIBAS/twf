Dictionary Workflows
====================

The Dictionary Workflows in TWF are designed to connect dictionary entries with external
authoritative data. These workflows support integration with the following external sources:

- **GND**: Gemeinsame Normdatei (Integrated Authority File)
- **Wikidata**: A free and open knowledge base
- **Geonames**: A geographical database
- **OpenAI**: AI-generated insights or suggestions

Workflow Types
--------------

Dictionary workflows are categorized into three types:

1. **Automated Workflows**
2. **Supervised Workflows**
3. **Manual Workflows**

### 1. Automated Workflows

Automated workflows establish connections between dictionary entries and authoritative data
without requiring user intervention. These workflows are ideal for large-scale, consistent data
synchronization.

**Key Features:**

- Bulk processing of dictionary entries.
- Automated matching based on predefined rules or heuristics.
- Minimal user input required.

**Implemented Automated Workflows:**

- **GND Integration**: Matches entries with GND records.
- **Wikidata Synchronization**: Connects entries with relevant Wikidata entities.
- **Geonames Matching**: Links geographical entries to Geonames.
- **OpenAI Suggestions**: Uses AI to suggest potential matches for entries.

**Requirements:**
- API-Keys or other access credentials for the respective sources. Set up in the project settings.
- Well-formed dictionary labels and entries to ensure accurate matching.

---

### 2. Supervised Workflows

Supervised workflows involve user oversight during the matching process. Users are prompted to
review and approve connections before they are finalized.

**Key Features:**

- User validation for each match.
- Provides a balance between automation and control.
- Recommended for scenarios where data quality is critical.

**Use Cases:**

- Reviewing ambiguous matches from automated workflows.
- Fine-tuning connections to ensure accuracy.

**Requirements:**
- API-Keys or other access credentials for the respective sources. Set up in the project settings.
- User intervention to validate or correct matches.

---

### 3. Manual Workflows

Manual workflows are fully user-driven, allowing for precise control over each connection.
Users manually link dictionary entries to authoritative data.

The manual workflows are suitable for small datasets or entries requiring detailed attention.
If you are creating your own authoritative data, you can use the manual workflows to establish
connections between your data and the dictionary entries.

**Key Features:**

- Full user control over every step.
- Suitable for small datasets or entries requiring detailed attention.
- No automation; every connection is explicitly defined by the user.

**Typical Workflow:**

1. Select a dictionary entry.
3. Manually create or select a matching entity.

---

Integration with Authoritative Data
-----------------------------------

The following sources are currently supported in TWF's dictionary workflows:

- **GND (Integrated Authority File)**:
  - Provides access to structured bibliographic and authority data.
  - Used for validating entities like persons, organizations, or places.

- **Wikidata**:
  - A collaborative knowledge graph for structured data.
  - Offers diverse information and connections for a wide range of entities.

- **Geonames**:
  - A geographical database that links dictionary entries to geographical locations.

- **OpenAI**:
  - AI-generated suggestions to identify potential matches or enrich entries.

---

Getting Started
---------------

1. Navigate to the **Dictionaries** section in TWF.
2. Select a workflow type: Automated, Supervised, or Manual.
3. Configure the workflow (e.g., select the authoritative source and matching criteria).
4. Start the workflow and monitor progress.

For more detailed information, see the specific documentation for each workflow type.
