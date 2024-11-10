What is TWF - Transkribus Workflow
==================================

TWF, or Transkribus Workflow, is a web service designed to streamline
the process of working with data from Transkribus, an OCR service, and other digital
collections. TWF simplifies and automates several key steps, allowing researchers
to focus on data analysis rather than data management.

The TWF workflow includes the following steps:

1. **Connect to Transkribus**:
   TWF establishes a secure connection to Transkribus using your stored credentials
   and triggers an export for a selected collection.

2. **Download the Result**:
   The exported data is automatically downloaded and prepared for further processing.

3. **Data Preparation**:

   - **Unpacking**:
     The downloaded files are unpacked and saved to the filesystem, making them
     accessible for parsing and further processing.

   - **Parsing Files**:
     TWF uses the ``simple-alto-parser`` library to extract structured information
     from ALTO XML or Page XML files, saving this information in the database.

4. **Tag Extraction**:
   Tags marked in Transkribus are extracted and stored in the database. TWF enables
   tags to be categorized by type and organized within dictionary entries.

5. **Metadata and Dictionary Management**:

   - **Dictionary Entries**:
     Entries can be created, grouped, and enriched with metadata, which is stored
     in the database. Dictionaries can contain various references and metadata types,
     allowing for nuanced organization.

   - **Metadata Handling**:
     TWF also supports custom metadata for both documents and pages, which can be
     loaded from JSON files or directly through the interface.

6. **Export and Analysis**:

   - **Customizable Exports**:
     Users can export data in various formats, such as JSON, CSV, or Excel. Export
     configurations are customizable, allowing for tailored data outputs to meet
     specific project requirements.

   - **Automated Enrichment**:
     TWF includes automated workflows for cross-referencing and enriching data with
     external sources (e.g., GND, Wikidata, Geonames, and OpenAI).

This end-to-end automation within TWF reduces manual steps, minimizes error potential,
and ensures data is consistently structured and ready for further analysis. With TWF,
researchers can focus on deriving insights from their data rather than managing it.
