Multimodal Workflows
==================

This guide provides practical workflows and examples for using the multimodal functionality in TWF. It demonstrates common use cases and best practices for combining text and images when querying AI providers.

Basic Workflow
-------------

The basic workflow for using multimodal functionality in TWF follows these steps:

1. Select documents with images that you want to analyze
2. Choose the appropriate AI provider (OpenAI, Claude, Gemini, Mistral)
3. Select the prompt mode (Text only, Images only, Text + Images)
4. Craft an effective prompt
5. Submit the query and review the results

Text + Images Analysis Workflow
-----------------------------

This workflow demonstrates how to analyze documents using both text and images:

Step 1: Select Documents
~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the Documents section
2. Use filters to find documents containing images
3. Select up to 5 documents to include in your analysis
4. Click "Continue to AI Query"

Step 2: Choose Provider and Mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Select the AI provider (e.g., OpenAI for GPT-4 Vision)
2. Choose "Text + Images" as the prompt mode
3. Note that the system will automatically select up to 5 images per document

Step 3: Craft an Effective Prompt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When combining text and images, craft prompts that:

1. Clearly state what information you want to extract
2. Provide context about the images
3. Ask specific questions
4. Request structured output if needed

Example prompt:

```
Analyze these document pages from a 19th century historical manuscript.
1. Identify the main topic of each page
2. Transcribe any visible text
3. Note any interesting visual elements (diagrams, illustrations, etc.)
4. Identify the approximate time period based on writing style and content
5. Return your analysis in a structured format with bullet points for each page
```

Step 4: Review Results
~~~~~~~~~~~~~~~~~~~

1. Review the AI's response
2. Save important insights to document metadata
3. Compare results between different AI providers if needed

Images-Only Workflow
-----------------

This workflow focuses on pure image analysis without providing additional text context:

Step 1: Select Documents
~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the Documents section
2. Select documents with high-quality images
3. Click "Continue to AI Query"

Step 2: Configure Query
~~~~~~~~~~~~~~~~~~~~

1. Select an AI provider with strong image analysis capabilities (Gemini or GPT-4 Vision)
2. Choose "Images only" as the prompt mode
3. Set a clear system prompt that provides general instructions

Example system prompt:

```
You are an expert document analyst with expertise in historical manuscripts, handwriting recognition, and visual document analysis. Thoroughly analyze the provided document images and describe their contents, focusing on both visual elements and any visible text. Provide a detailed analysis of each image.
```

Step 3: Review Results
~~~~~~~~~~~~~~~~~~~

1. Review the AI's analysis of purely visual content
2. Save important insights to document metadata
3. Use insights for document classification or tagging

Practical Examples
----------------

Example 1: Historical Document Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: You have scanned historical documents and want to extract key information.

**Provider**: Claude 3

**Prompt Mode**: Text + Images

**Prompt**:
```
Analyze these historical document scans. For each document:
1. Identify the document type (letter, certificate, ledger, etc.)
2. Extract names of key individuals mentioned
3. Identify locations mentioned
4. Determine the approximate date of creation
5. Note any official seals, letterheads, or distinguishing marks
6. Transcribe any particularly important passages
```

Example 2: Handwritten Text Recognition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: You need to transcribe handwritten documents.

**Provider**: GPT-4 Vision

**Prompt Mode**: Images only

**System Prompt**:
```
You are an expert in paleography and handwriting recognition across multiple languages and historical periods. Carefully transcribe any handwritten text visible in the provided images. If portions are illegible, indicate this with [illegible]. If you're uncertain about a word, provide your best guess followed by [?]. Maintain original paragraph breaks and formatting where possible.
```

Example 3: Document Classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: You need to categorize a large collection of documents.

**Provider**: Gemini

**Prompt Mode**: Text + Images

**Prompt**:
```
Classify each document into one of the following categories:
- Financial Record
- Personal Correspondence
- Legal Document
- Official Certificate
- Academic Text
- Religious Document
- Other (specify)

For each document, provide:
1. The category
2. Confidence level (High/Medium/Low)
3. Key identifying features that led to this classification
4. Any subcategories that might apply
```

Advanced Techniques
-----------------

Combining Multiple AI Providers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For critical analysis, consider using multiple AI providers:

1. Start with an Image-only analysis using Gemini
2. Follow with a Text+Images analysis using Claude 3
3. Finish with a detailed Text+Images analysis using GPT-4 Vision
4. Compare and combine the insights from all three providers

Image Selection Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~

The default system selects up to 5 images per document, but you can optimize this:

1. For dense text documents, pre-select the most informative pages
2. For visual analysis, ensure selected images contain the relevant visual elements
3. Remember that image quality affects AI performance

Prompt Engineering for Multimodal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Effective multimodal prompts have these characteristics:

1. **Clear Instructions**: Explicitly tell the AI what to look for in both text and images
2. **Context Provision**: Explain what type of documents you're providing
3. **Structured Output Requests**: Ask for responses in a specific format (tables, lists, etc.)
4. **Visual Attention Direction**: Direct attention to specific visual elements when needed

Example advanced prompt:

```
I'm providing pages from a historical shipping manifest from approximately 1850-1870.

First, analyze the overall document structure by identifying:
- Header information (ship name, dates, ports)
- Column structure 
- Any official stamps or seals

Next, extract the following data in tabular format:
| Ship Name | Departure Date | Arrival Date | Origin Port | Destination Port | Cargo Types |

Pay special attention to the handwritten annotations in the margins, which often contain important corrections or additional information.

If you encounter unfamiliar abbreviations or specialized maritime terminology, provide your best interpretation and indicate your confidence level.
```

Troubleshooting
-------------

Poor Quality Results
~~~~~~~~~~~~~~~~~

If you're getting poor quality results:

1. **Image Quality**: Check if the images are clear enough for analysis
2. **Image Selection**: Ensure relevant pages are being selected
3. **Provider Selection**: Try a different AI provider that might be stronger for your specific use case
4. **Prompt Clarity**: Make your instructions more explicit and detailed
5. **System Prompt**: Adjust the system prompt to better guide the AI

Token Limitations
~~~~~~~~~~~~~~

When hitting token limitations:

1. Reduce the number of images included
2. Use image scaling to reduce image size
3. Focus your prompt on the most important information
4. Split the analysis into multiple smaller queries

Error Resolution
~~~~~~~~~~~~~

Common errors and solutions:

1. **Provider API errors**: Check API credentials in project settings
2. **Image format errors**: Ensure images are in a supported format (JPG, PNG)
3. **Timeout errors**: Reduce the number of images or the complexity of the query
4. **Connection errors**: Check network connectivity and API endpoint availability