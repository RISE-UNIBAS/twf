Project AI Views
==============

AI Query Views
------------

TWF provides specialized views for interacting with AI models at the project level.
These views present forms that allow users to:

1. Select which project documents to include in the AI query
2. Choose the sending mode (text-only, images-only, or text+images) for multimodal models
3. Customize the prompt and system role description
4. Submit the query for asynchronous processing

Multimodal Capabilities
----------------------

The AI query views support different levels of multimodal processing depending on the
AI provider:

- **OpenAI**: Full support for text-only, images-only, and mixed text+images modes
- **Google Gemini**: Full support for all three multimodal modes
- **Claude**: Currently limited to text-only mode
- **Mistral**: Currently limited to text-only mode

For modes that include images, the system automatically selects up to 5 images per document
from the specified documents, retrieving them directly from the Transkribus server.

.. automodule:: twf.views.project.views_project_ai
   :members:
   :undoc-members:
   :show-inheritance: