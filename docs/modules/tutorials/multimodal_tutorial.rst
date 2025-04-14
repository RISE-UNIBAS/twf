Multimodal Tutorial
===================

This step-by-step tutorial guides you through a complete multimodal workflow in TWF, from selecting documents to analyzing AI responses.

Tutorial Overview
-----------------

In this tutorial, you'll learn how to:

1. Select appropriate documents with images
2. Configure a multimodal AI query
3. Craft effective prompts for text and image analysis
4. Submit queries to different AI providers
5. Interpret and utilize the results

By the end, you'll be able to effectively combine text and images in your AI workflows.

Prerequisites
-------------

Before starting this tutorial, make sure you have:

1. **TWF** Access**: A working TWF installation with appropriate* permissions**
2. **API** Keys**: Valid API keys configured for at least one AI* provider**
3. **Documents**: A few test documents with images uploaded to your* project**
4. **Basic** Knowledge**: Familiarity with the TWF interface and document* management**

Step 1: Preparing Your Documents
--------------------------------

First, let's prepare suitable documents for multimodal analysis:

1. **Navigate* to** Documents** by clicking the "Documents" tab in the main navigation*.**

2. **Select Documents with* High-Quality** Images**:**
   - Look for documents that have clear, high-resolution images
   - Ideally, select 2-3 documents of the same type (e.g., historical manuscripts, technical diagrams)
   - Check image quality by previewing document pages

3. **Check* Document** Metadata**:**
   - Ensure documents have basic metadata filled out
   - This will help provide context for the AI

Document Selection Tips:
   - Choose documents with a mix of text and visual elements
   - Select documents that pose interesting analytical questions
   - Consider thematically related documents for comparative analysis

Step 2: Configuring a Basic Multimodal Query
--------------------------------------------

Now let's set up a basic multimodal query:

1. **Navigate to* AI** Query**:**
   - From the Documents view, select your chosen documents
   - Click "Actions" → "AI Query"

2. **Select Provider* and** Mode**:**
   - Choose "OpenAI" as your AI provider (GPT-4 Vision has strong multimodal capabilities)
   - Select "Text + Images" as the prompt mode
   - Note that the system will automatically select up to 5 images from each document

3. **Configure* Basic** Settings**:**
   - Set an appropriate role description (e.g., "You are an expert document analyst specializing in historical manuscripts")
   - Leave other settings at their defaults for now

4. **Craft a* Simple** Prompt**:**
   For your first query, use this basic prompt:

   ```
   Please analyze these document pages and provide:
   1. A brief description of what each page contains
   2. Any interesting visual elements you notice
   3. The main subject matter of each page
   4. Any text that you can identify or transcribe
   
   Organize your response by page number.
   ```

5. **Submit* the** Query**:**
   - Review your configuration one last time
   - Click "Submit Query"
   - Note that processing may take a minute or two depending on the number of images

Step 3: Analyzing the Results
-----------------------------

Once the query completes, let's analyze the results:

1. **Review* the** Response**:**
   - Read through the AI's analysis of each page
   - Note how it identifies both textual and visual elements
   - Pay attention to how it organizes information by page

2. **Evaluate** Accuracy**:**
   - Compare the AI's descriptions to the actual document pages
   - Note any misinterpretations or omissions
   - Pay special attention to text transcription accuracy

3. **Save* Important** Insights**:**
   - Use the "Save to Metadata" option to store valuable insights
   - Select key sections of the response to save
   - Add to appropriate metadata fields (e.g., "AI Analysis", "Transcription")

Step 4: Crafting Specialized Queries
------------------------------------

Now let's create more specialized queries to get deeper insights:

1. **Visual* Element** Analysis**:**
   
   Try an image-focused query using "Images only" mode:
   
   ```
   Focus only on the visual elements in these documents:
   1. Identify any diagrams, illustrations, or non-text elements
   2. Describe the style and technique of any illustrations
   3. Note any symbols, seals, or distinctive marks
   4. Analyze the layout and visual organization of each page
   
   Be as detailed as possible in your visual analysis.
   ```

2. **Text* Transcription** Query**:**
   
   Try a text-focused query while still in multimodal mode:
   
   ```
   Please focus on accurately transcribing any text in these documents:
   1. Transcribe all visible text, maintaining original formatting where possible
   2. For difficult or unclear text, indicate uncertainty with [?]
   3. For completely illegible sections, use [illegible]
   4. Note any unusual spellings or archaic language
   
   Present the transcription separately for each page.
   ```

3. **Comparative** Analysis**:**
   
   If you selected related documents, try this comparative query:
   
   ```
   Compare and contrast the documents I've provided:
   1. Identify similarities in content, style, and format
   2. Note key differences between the documents
   3. Suggest if they might be related, created by the same author, or from the same time period
   4. Highlight any progression or sequence if these seem to be related documents
   
   Provide specific examples from the images to support your analysis.
   ```

Step 5: Experimenting with Different AI Providers
-------------------------------------------------

Let's compare results from different AI providers:

1. **Claude** Query**:**
   - Return to the AI Query page
   - Select the same documents
   - Choose "Claude" as the provider
   - Use the same prompt from your first OpenAI query
   - Submit and compare results with OpenAI's response

2. **Gemini** Query**:**
   - Repeat with Gemini as the provider
   - Use the same prompt again
   - Submit and add this to your comparison

3. **Compare* Provider** Strengths**:**
   - Note which provider gave the most accurate text transcription
   - Compare visual analysis capabilities
   - Observe differences in response structure and detail
   - Consider which provider would be best for your specific use case

Step 6: Advanced Prompt Engineering
-----------------------------------

Now let's refine our prompts for better results:

1. **Structured* Output** Prompt**:**
   
   Try this prompt designed to get more structured results:
   
   ```
   Analyze these document pages and provide your response in the following structured format:
   
   For each page:
   
   ## Page [Number]
   
   ### Visual Elements
   - [List all diagrams, illustrations, and visual elements]
   
   ### Content Summary
   - [2-3 sentence summary of the page content]
   
   ### Full Transcription
   ```
   [Transcribed text with original formatting]
   ```
   
   ### Notable Features
   - [List any unusual or interesting features]
   
   ### Estimated Date/Period
   - [Your best estimate with reasoning]
   ```

2. **Expert* Role** Prompt**:**
   
   Try enhancing the system prompt with more expertise:
   
   First, set this as your role description:
   
   ```
   You are an expert paleographer and historical document analyst with 30 years of experience analyzing manuscripts from the 15th to 19th centuries. You have particular expertise in handwriting analysis, dating documents based on physical characteristics, and identifying document types based on layout and formatting. You always provide detailed, evidence-based analysis and clearly indicate your level of certainty about conclusions.
   ```
   
   Then use this as your prompt:
   
   ```
   Provide a professional analysis of these historical document pages, including:
   
   1. Document classification (type, purpose, approximate period)
   2. Detailed transcription of text content
   3. Analysis of handwriting style and characteristics
   4. Identification of any official marks, seals, or signatures
   5. Assessment of the document's condition and completeness
   6. Any notable or unusual features
   
   Include your confidence level for each conclusion and explain your reasoning.
   ```

Step 7: Saving and Utilizing Results
------------------------------------

Finally, let's put the insights to use:

1. **Create* Document** Tags**:**
   - Based on AI analysis, create appropriate tags for your documents
   - For example: "Contains_Illustrations", "19th_Century", "Handwritten"
   - Use the Tags management interface to add these tags

2. **Update** Metadata**:**
   - Add key information to document metadata fields
   - For example, add transcribed text to a "Transcription" field
   - Add visual descriptions to a "Visual Elements" field

3. **Create* Analysis** Notes**:**
   - Compile the most valuable insights into document notes
   - Summarize findings across different AI providers
   - Note which providers performed best for which tasks

4. **Save* Effective** Prompts**:**
   - Save your most effective prompts for future use
   - Create a prompt library in your project settings
   - Document which prompts work best for which document types

Advanced Applications
---------------------

Here are some advanced applications to try after completing the basic tutorial:

1. **Document* Classification** Workflow**:**
   - Use multimodal queries to automatically classify documents
   - Create a classification prompt that assigns categories
   - Use results to tag and organize your document collection

2. **Transcription** Verification**:**
   - Compare transcriptions across multiple AI providers
   - Use differences to identify potentially problematic text
   - Create a consensus transcription from multiple results

3. **Visual* Element** Extraction**:**
   - Use image-only queries to catalog visual elements
   - Create a database of illustrations, seals, or other visual elements
   - Link these to appropriate metadata for search and retrieval

4. **Historical* Context** Enhancement**:**
   - Use multimodal AI to suggest historical context
   - Add this information to document descriptions
   - Build relationships between documents based on AI-suggested connections

5. **Batch* Processing** Workflow**:**
   - Apply successful prompts to larger document batches
   - Use Celery tasks to process documents asynchronously 
   - Automatically tag and categorize based on results

Troubleshooting Common Issues
-----------------------------

If you encounter issues during this tutorial:

1. **Long* Processing** Times**:**
   - Reduce the number of images selected
   - Use a smaller prompt
   - Check system resources and network connectivity

2. **Poor* Quality** Responses**:**
   - Check image quality and resolution
   - Try a different AI provider
   - Be more specific in your prompt
   - Provide more context about the document type

3. **API** Errors**:**
   - Verify your API keys in project settings
   - Check provider service status
   - Ensure you have sufficient API quota/credits

4. **Interface** Issues**:**
   - Try refreshing the page
   - Clear browser cache
   - Use a supported browser (Chrome recommended)

Conclusion
----------

In this tutorial, you've learned how to:

1. Select appropriate documents for multimodal analysis
2. Configure basic and advanced multimodal queries
3. Craft effective prompts for different analysis types
4. Compare results across different AI providers
5. Save and utilize the insights gained

Remember that effective multimodal analysis involves balancing text and image components, providing clear instructions, and selecting the right AI provider for each specific task. As you practice, you'll develop a sense for which approaches work best for your particular document types.