Multimodal Frequently Asked Questions
=====================================

This document addresses common questions about the multimodal functionality in TWF.

General Questions
-----------------

What is multimodal AI functionality?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multimodal AI functionality refers to the ability to process and analyze both text and images together. In TWF, this allows you to send document images along with text prompts to AI providers for analysis, getting richer insights than would be possible with text-only queries.

Which AI providers support multimodal functionality?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TWF currently supports multimodal functionality with the following providers:

* **OpenAI**: GPT-4 Vision supports text and* images**
* **Anthropic** Claude**: Version 3 and above support multimodal* prompts**
* **Google** Gemini**: All models support multimodal* inputs**
* **Mistral**: Limited support in larger* models**

Which file formats are supported for images?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The supported image formats depend on the AI provider:

* **All** providers**: JPG/JPEG,* PNG**
* **OpenAI* &** Claude**: Additionally support* WebP**
* **Gemini**: Additionally supports GIF (static images* only)**

Is there a limit to how many images I can include?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, there are limits:

* TWF limits: By default, up to 5 images per document and 10 images total per request*
* Provider limits:*
  - OpenAI: ~20 images per request (depends on size)
  - Claude: ~10 images per request (depends on size)
  - Gemini: ~16 images per request
  - Mistral: 2-3 images per request

How are images selected from my documents?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the system:
1. Takes up to 5 images per document
2. Selects images based on page number order (first 5 pages)
3. Scales images appropriately based on provider requirements
4. Uses direct URLs rather than downloading images locally

Usage Questions
---------------

How do I enable multimodal functionality?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multimodal functionality is enabled by default when you select a provider that supports it. To use it:

1. Select documents with images
2. Choose a supported AI provider
3. Select a prompt mode (Text only, Images only, or Text + Images)
4. Craft an appropriate prompt
5. Submit the query

What's the difference between the different prompt modes?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The three prompt modes control what content is sent to the AI:

* **Text** only**: Only sends your text prompt (no* images)**
* **Images** only**: Sends only images with a minimal* prompt**
* **Text* +** Images**: Sends both your text prompt and selected* images**

When should I use each prompt mode?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose your prompt mode based on your specific needs:

* **Text** only**: When your query is about text content or metadata and doesn't require visual* analysis**
* **Images** only**: When you want the AI to focus entirely on visual analysis without being influenced by your text* prompt**
* **Text* +** Images**: For most mixed content analysis, when you want to guide the AI's analysis of the images with specific* questions**

How do I write effective prompts for multimodal queries?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For effective multimodal prompts:

1. Be specific about what aspects of the images you want analyzed
2. Number your questions or instructions for clearer responses
3. Provide context about the document type and time period
4. Request structured output formats when appropriate
5. Ask the AI to explain its reasoning and confidence level

See the Multimodal Best Practices document for detailed guidance.

Can I use multimodal functionality with collections?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, you can use multimodal functionality with collections:

1. Select a collection instead of individual documents
2. The system will process collection items as it would documents
3. You can set collection-specific processing parameters in project settings

Technical Questions
-------------------

How are images sent to the AI providers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Images can be sent in two ways:

1. **URL-based** (preferred): The system sends the image URL directly to the AI* provider**
   - Advantages: Faster, no local storage needed
   - Used when images are available via accessible URLs

2. **Base64-encoded** (fallback): The system encodes the image* data**
   - Used when direct URLs aren't available
   - More bandwidth-intensive but works for all providers

What image scaling options are available?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TWF provides several scaling options via the IIIF protocol:

* **Percentage** scaling**: Reduce to a percentage of original size (e.g., 50%,* 25%)**
* **Width-based** scaling**: Scale to a specific width in* pixels**
* **Height-based** scaling**: Scale to a specific height in* pixels**
* **Maximum* dimension** scaling**: Scale based on the maximum* dimension**

The default is 50% scaling, which works well for most use cases.

How does token usage work with multimodal queries?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multimodal queries generally use more tokens than text-only queries:

* Images are converted to tokens based on their size and complexity*
* A typical image might use 300-1000 tokens depending on the provider*
* Larger images use more tokens*
* Each provider has different tokenization methods for images*

To optimize token usage:
1. Scale images appropriately
2. Use only the necessary number of images
3. Be concise in your prompts

How secure is the multimodal functionality?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Security considerations for multimodal functionality:

* Image URLs are transmitted to third-party AI providers*
* Data transmission uses HTTPS encryption*
* API keys are securely stored in the database*
* Provider privacy policies apply to transmitted content*
* No permanent storage of images or results by providers (but check provider-specific policies)*

Provider-Specific Questions
---------------------------

OpenAI (GPT-4 Vision)
~~~~~~~~~~~~~~~~~~~~~

**Q: Which OpenAI models* support** multimodal?**
A: Currently, only GPT-4 Vision and GPT-4o support image inputs. Other models like GPT-3.5 Turbo are text-only.

**Q: What are the image size limits* for** OpenAI?**
A: OpenAI recommends images under 20MB and recommends using the 512x512 resolution for most purposes.

**Q: How many images can I send to OpenAI* at** once?**
A: While technically possible to send many images, practical limits are around 20 images per request due to token limitations.

Claude
~~~~~~

**Q: Which Claude models* support** multimodal?**
A: Claude 3 models (Opus, Sonnet, and Haiku) support multimodal inputs. Older Claude versions do not.

**Q: Does Claude require specific* image** formats?**
A: Claude requires the media_type to be specified for images. TWF automatically handles this based on the file extension.

**Q: Is Claude good at analyzing documents* with** text?**
A: Yes, Claude excels at document analysis and text recognition in images, often providing detailed transcriptions.

Gemini
~~~~~~

**Q: How does Gemini handle* images** differently?**
A: Gemini processes images using a different underlying architecture (PaLM) that's specifically designed for multimodal content.

**Q: Does Gemini support* animated** GIFs?**
A: Gemini can accept GIF files but only processes them as static images (first frame).

**Q: What are Gemini's strengths for* multimodal** analysis?**
A: Gemini is particularly strong at visual recognition tasks and identifying objects/elements in images.

Mistral
~~~~~~~

**Q: Why is Mistral's multimodal support listed* as** "limited"?**
A: Mistral's multimodal capabilities are newer and currently support fewer images per request than other providers.

**Q: Which Mistral models* support** images?**
A: Currently, only Mistral Large supports images. Small and Medium models are text-only.

**Q: Should I use Mistral for* multimodal** analysis?**
A: For multimodal analysis, Mistral is generally not as capable as other providers. It's better suited for text analysis with occasional image support.

Troubleshooting
---------------

Why am I getting "Provider does not support multimodal" errors?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This error occurs when:
1. You've selected a provider that doesn't support multimodal (e.g., older Claude versions)
2. You've selected a model that doesn't support multimodal (e.g., GPT-3.5 Turbo)
3. The provider's multimodal API is temporarily unavailable

Solution: Select a compatible provider or switch to text-only mode.

Why are my images not appearing in the response?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the AI doesn't seem to acknowledge the images:

1. Check that you've selected "Images only" or "Text + Images" mode
2. Verify that your documents actually contain images
3. Ensure the images are in a supported format
4. Check if you've exceeded the provider's image limit
5. Make your prompt explicitly reference the images

Why is the image analysis quality poor?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Poor image analysis can result from:

1. Low resolution or unclear images
2. Images without sufficient visual features of interest
3. Prompt that doesn't guide the AI to focus on relevant aspects
4. Provider limitations in analyzing your specific image type

Solutions:
- Try a different AI provider
- Improve image quality if possible
- Be more specific in your prompt about what to analyze
- Consider using a specialized computer vision service instead

Best Practices
--------------

What's the optimal image resolution for AI analysis?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The optimal resolution depends on the content type:

* **Text** documents**: At least 300 DPI for text* recognition**
* **Visual** content**: 150-300 DPI is usually* sufficient**
* **Technical** diagrams**: Higher resolution (300-600 DPI) for fine* details**

However, very high resolutions waste tokens, so balance quality with efficiency.

How many images should I include in a single query?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For best results:

* **Focused** analysis**: 1-3 images for detailed* analysis**
* **Document** comparison**: 2-5 images for comparison* tasks**
* **Batch** processing**: 5-10 images for overview* analysis**

More images means:
- Higher token usage
- Potentially less detailed analysis per image
- Longer processing times

What's the best way to combine text and images in prompts?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For effective text+image prompts:

1. Clearly reference the images in your text (e.g., "In the provided images...")
2. Number your questions for clearer responses
3. Ask specific questions about visual elements
4. Request the AI to explain connections between visual elements and text
5. For multiple images, ask for comparisons when relevant