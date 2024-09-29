What is TWF - Transkribus Workflow
==================================

TWF, or Transkribus Workflow, is a webservice designed to streamline the process of
working with Transkribus exports. It automates several steps in the export process,
making it easier and more efficient to use further work with your Transkribus data.

The workflow includes the following steps:

1. Connect to Transkribus: The service establishes a connection to Transkribus
   using your provided credentials and triggers an export of a collection.

2. Download the result: The exported data is then downloaded for further processing.

3. Unpack the result: The downloaded data is unpacked and its contents are saved to the
   filesystem, ready for parsing.

4. The files are parsed using the simple-alto-parser library, which extracts the
   relevant information from the Page.xml files and saves it in a structured format
   to a database.

5. Tags marked in Transkribus are extracted and saved to the database. They can be grouped
   by type and can be further grouped in dictionary entries.

6. The dictionary entries can be enriched with metadata and saved to the database.


This automated workflow saves time and reduces the potential for errors that can occur when
these steps are performed manually. With TWF, you can focus more on using the data and less
on the logistics of obtaining and preparing it.