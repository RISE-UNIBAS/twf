Clients
=======

The TWF application uses various client modules to interact with external services and APIs. These clients provide abstracted interfaces for communicating with different services, including AI providers, geographical databases, and data sources.

AI Clients
---------

The AI clients provide interfaces to various AI service providers, including multimodal capabilities for combining text and images in prompts.

.. toctree::
   :maxdepth: 1
   :caption: AI Client Documentation

   clients/simple_ai.rst
   clients/multimodal_comparison.rst

External Data Clients
--------------------

These clients connect to external data sources for normalized information:

.. toctree::
   :maxdepth: 1
   :caption: External Data Clients

   clients/geonames.rst
   clients/gnd.rst
   clients/wikidata.rst

Other Clients
------------

Additional utility clients:

.. toctree::
   :maxdepth: 1
   :caption: Other Clients

   clients/google_sheets.rst