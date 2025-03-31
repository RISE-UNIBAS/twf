Multimodal AI Features
====================

Overview
--------

TWF integrates multimodal AI capabilities, allowing you to send both text and images 
to AI providers that support it. This feature is particularly useful for analyzing 
historical documents where the visual appearance of the page may contain important 
information beyond the extracted text.

Supported AI Providers
---------------------

TWF currently supports the following AI providers with varying levels of multimodal capabilities:

1. **OpenAI (GPT-4 Vision)**
   - Full support for text+images
   - Images can be sent directly from Transkribus servers
   - No need to download images locally

2. **Google Gemini**
   - Native multimodal capabilities
   - Excellent image understanding
   - Seamless integration of text and image context

3. **Anthropic Claude**
   - Currently limited to text-only mode in TWF
   - Native API does support images, but this is not currently enabled

4. **Mistral**
   - Text-only support
   - No current multimodal capabilities

Sending Modes
------------

When using multimodal-capable providers (OpenAI and Gemini), you can choose from three different sending modes:

- **Text Only**: Sends only the text content from the selected documents, not including any images.
- **Images Only**: Sends only images from the selected documents, with minimal text instructions.
- **Text + Images**: Sends both the text content and images from the selected documents.

Image Selection
--------------

When using modes that include images:

- TWF automatically selects up to 5 images per document from the documents you choose
- Images are taken in order of page number
- Images are retrieved directly from the Transkribus server using IIIF URLs
- You can configure the image scaling to optimize for quality vs. API costs
- No need to manually select individual pages

Implementation Details
--------------------

The multimodal functionality is implemented through several key components:

1. **User Interface**:
   - The form in project AI views allows selection of documents and sending mode
   - Clear messaging about which AI providers support multimodal features

2. **Image Handling**:
   - The Page model provides methods to access image URLs with optional scaling
   - The AiApiClient class handles both local files and remote URLs

3. **Task Processing**:
   - The process_single_ai_request method manages different sending modes
   - The task checks provider capabilities and falls back to text-only when needed

4. **API Integration**:
   - Each provider has specific handling for multimodal content
   - OpenAI and Gemini both accept direct image URLs without needing to download