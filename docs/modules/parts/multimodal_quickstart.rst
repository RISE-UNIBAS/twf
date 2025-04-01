Multimodal Quickstart Guide
========================

This quickstart guide provides the essentials for using the multimodal functionality in TWF.

Setup in 5 Minutes
----------------

1. **Check API Key**:
   - Navigate to Project Settings → Credentials
   - Ensure you have at least one AI provider API key configured
   - OpenAI (GPT-4 Vision) is recommended for first-time users

2. **Select Documents**:
   - Go to the Documents section
   - Select 1-3 documents with images
   - Click Actions → AI Query

3. **Configure Query**:
   - Select an AI provider (e.g., OpenAI)
   - Choose "Text + Images" as the prompt mode
   - Enter a descriptive role (e.g., "You are an expert document analyst")

4. **Enter Prompt**:
   - Use this starter prompt:
   ```
   Analyze these document pages and describe:
   1. The main content of each page
   2. Any interesting visual elements
   3. Any text you can identify
   ```

5. **Submit Query**:
   - Click "Submit Query"
   - Wait for processing (usually 30-60 seconds)
   - Review the results

That's it! You've completed your first multimodal query.

Key Features
----------

- **Three Prompt Modes**: Text only, Images only, or Text + Images
- **Automatic Image Selection**: System selects up to 5 images per document
- **Provider Selection**: Choose from OpenAI, Claude, Gemini, or Mistral
- **Scaling Options**: Images are appropriately scaled for each provider
- **Asynchronous Processing**: Tasks run in the background via Celery

Essential Tips
-----------

For best results:

1. **Be Specific**: Clearly state what you want the AI to analyze
2. **Use Structure**: Number your questions or requests
3. **Provider Selection**: 
   - OpenAI: Best for general-purpose analysis
   - Claude: Excellent for text in images
   - Gemini: Strong visual recognition
   - Mistral: Better for text with minimal images

4. **Image Selection**: Choose documents with clear, high-quality images
5. **Response Storage**: Use "Save to Metadata" to store valuable insights

Next Steps
--------

- Try the comprehensive [Multimodal Tutorial](../tutorials/multimodal_tutorial.html)
- Read [Best Practices](multimodal_best_practices.html) for advanced techniques
- Check the [FAQ](multimodal_faq.html) for common questions
- Review [Configuration Options](multimodal_config.html) for customization

Sample Prompts
------------

**Document Overview**:
```
Provide a concise overview of each document page, describing both textual and visual elements.
```

**Detailed Text Analysis**:
```
Focus on the text content in these documents:
1. Transcribe any visible text, maintaining formatting where possible
2. Identify key information (names, dates, locations)
3. Note any unusual terminology or abbreviations
```

**Visual Element Focus**:
```
Analyze only the visual elements in these documents:
1. Identify all non-text elements (diagrams, illustrations, seals, etc.)
2. Describe their appearance and potential purpose
3. Note any visual patterns across multiple pages
```

**Comparative Analysis**:
```
Compare and contrast the documents I've provided:
1. Note similarities and differences in content and format
2. Suggest if they appear to be related or from the same source
3. Identify any sequence or progression if they seem connected
```

Quick Troubleshooting
-------------------

**Issue**: Response ignores images
**Solution**: Verify you selected "Images only" or "Text + Images" mode

**Issue**: Poor quality analysis
**Solution**: Try a different AI provider or be more specific in your prompt

**Issue**: Processing takes too long
**Solution**: Reduce the number of documents/images or simplify your prompt

**Issue**: API errors
**Solution**: Check your API key configuration in project settings