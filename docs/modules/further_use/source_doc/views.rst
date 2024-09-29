Views
======
Views are the main part of the application. They are responsible for handling the requests and
responses of the application. The views are divided into several modules, each of which is
responsible for a specific part of the application. The main views are located in the `views`
directory of the application.

TWF uses class-based views. There is a `TWFView` class that is the base class for all views.
Each "section" (e.g. a main navigation item) has its own view class that inherits from `TWFView`.

.. toctree::
   :maxdepth: 1
   :caption: Views modules

   views/base.rst
   views/home.rst
   views/project.rst
   views/documents.rst
   views/tags.rst
   views/metadata.rst
   views/dictionaries.rst
   views/collections.rst
   views/export.rst

