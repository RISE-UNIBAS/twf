Multimodal Troubleshooting
==========================

This guide provides solutions to common issues encountered when using the multimodal functionality in TWF.

Common Problems and Solutions
-----------------------------

Provider API Errors
~~~~~~~~~~~~~~~~~~~

**Problem**: You receive errors related to the AI provider API.

**Solutions**:
1. Check API credentials in project settings
2. Verify API key format and permissions
3. Check for provider service disruptions
4. Ensure your account has sufficient credits/quota
5. Check if your API key has the necessary permissions for multimodal APIs

Specific error messages and solutions:

+--------------------------------------------+-----------------------------------------------+
| Error Message                              | Solution                                      |
+============================================+===============================================+
| "Invalid API key provided"                 | Update API key in project settings            |
+--------------------------------------------+-----------------------------------------------+
| "You exceeded your current quota"          | Purchase additional credits or wait for quota |
|                                            | to reset                                      |
+--------------------------------------------+-----------------------------------------------+
| "Model not found"                          | Check if you're using a valid model name for  |
|                                            | multimodal queries                            |
+--------------------------------------------+-----------------------------------------------+
| "This model does not support images"       | Switch to a model that supports multimodal    |
|                                            | inputs                                        |
+--------------------------------------------+-----------------------------------------------+

Image-Related Issues
~~~~~~~~~~~~~~~~~

**Problem**: Issues with image processing or display.

**Solutions**:
1. Check image format (JPG, PNG, etc.)
2. Verify image size is within provider limits
3. Check image URL accessibility
4. Ensure image loading is not blocked by CORS policies

Specific image issues:

+--------------------------------------------+-----------------------------------------------+
| Issue                                      | Solution                                      |
+============================================+===============================================+
| "Unable to access image URL"               | Check if the image URL is publicly accessible |
+--------------------------------------------+-----------------------------------------------+
| "Image too large"                          | Reduce image size or use scaling parameter    |
+--------------------------------------------+-----------------------------------------------+
| "Invalid image format"                     | Convert to a supported format (JPG, PNG)      |
+--------------------------------------------+-----------------------------------------------+
| "Too many images in request"               | Reduce the number of selected documents or    |
|                                            | pages                                         |
+--------------------------------------------+-----------------------------------------------+

Token Limit Exceeded
~~~~~~~~~~~~~~~~~~~~

**Problem**: Your request exceeds the token limit for the AI provider.

**Solutions**:
1. Reduce the number of images
2. Use image scaling to reduce image size
3. Shorten your text prompt
4. Split your query into multiple smaller queries
5. Use a provider with larger token limits

Performance Issues
~~~~~~~~~~~~~~~~~~

**Problem**: Slow processing times or timeouts.

**Solutions**:
1. Reduce the number of images
2. Use smaller or scaled images
3. Use provider-specific optimizations (e.g., setting max_tokens)
4. Check network connectivity
5. Try at a different time when provider load might be lower

Quality Issues
~~~~~~~~~~~~~~

**Problem**: Poor quality responses from the AI.

**Solutions**:
1. Improve image quality/resolution
2. Select better representative images
3. Improve prompt clarity and specificity
4. Try a different AI provider
5. Add more context in your prompt

Specific quality issues:

+--------------------------------------------+-----------------------------------------------+
| Issue                                      | Solution                                      |
+============================================+===============================================+
| AI ignores images in response              | Make explicit references to images in prompt  |
+--------------------------------------------+-----------------------------------------------+
| Incorrect text recognition                 | Use higher resolution images or try different |
|                                            | provider                                      |
+--------------------------------------------+-----------------------------------------------+
| Inconsistent analysis                      | Break analysis into more specific queries     |
+--------------------------------------------+-----------------------------------------------+
| Response too general                       | Ask more specific questions about the images  |
+--------------------------------------------+-----------------------------------------------+

User Interface Issues
~~~~~~~~~~~~~~~~~~~~~

**Problem**: Issues with the multimodal UI controls.

**Solutions**:
1. Check browser compatibility (Chrome recommended)
2. Clear browser cache and cookies
3. Check for JavaScript errors in browser console
4. Verify proper loading of UI assets

Provider-Specific Troubleshooting
-------------------------------

OpenAI (GPT-4 Vision)
~~~~~~~~~~~~~~~~~~~

Common issues:

1. **Error**: "This model does not support vision inputs"
   **Solution**: Ensure you're using GPT-4 Vision API, not standard GPT-4

2. **Error**: "Maximum context length exceeded"
   **Solution**: Reduce the number of images or use smaller images

3. **Error**: "Request timed out"
   **Solution**: Reduce the complexity of your query or number of images

Claude
~~~~~~

Common issues:

1. **Error**: "Media type required for image"
   **Solution**: Ensure proper media type detection is implemented

2. **Error**: "Bad Request: Invalid content format"
   **Solution**: Check the format of your content array in the request

3. **Error**: "Token limit exceeded"
   **Solution**: Claude has specific token limits; reduce content size

Gemini
~~~~~~

Common issues:

1. **Error**: "RESOURCE_EXHAUSTED"
   **Solution**: Gemini has quota limits; wait or request increased quota

2. **Error**: "INVALID_ARGUMENT"
   **Solution**: Check image format compatibility with Gemini

3. **Error**: "FAILED_PRECONDITION"
   **Solution**: Ensure Gemini API is enabled for your project

Mistral
~~~~~~~

Common issues:

1. **Error**: "Unsupported model for multimodal"
   **Solution**: Only Mistral Large supports multimodal; switch models

2. **Error**: "Invalid image format"
   **Solution**: Use supported format (JPG/PNG) and check encoding

3. **Error**: "Request entity too large"
   **Solution**: Mistral has more limited image size constraints; reduce image size

Advanced Troubleshooting
------------------------

System-Level Diagnosis
~~~~~~~~~~~~~~~~~~~

For persistent issues, perform a system-level diagnosis:

1. Check Celery task logs for detailed error information:
   ```
   grep "multimodal" logs/celery.log
   ```

2. Verify network connectivity to AI provider endpoints:
   ```
   curl -I https://api.openai.com
   curl -I https://api.anthropic.com
   curl -I https://generativelanguage.googleapis.com
   curl -I https://api.mistral.ai
   ```

3. Check for system resource constraints:
   ```
   top
   df -h
   free -m
   ```

Debug Mode
~~~~~~~~~~

Enable debug mode for more detailed logging:

1. In your project settings:
   ```python
   # Enable debug logging for multimodal functionality
   MULTIMODAL_DEBUG = True
   ```

2. Check debug logs in the browser console (for UI issues)
   
3. Add the debug parameter to your requests:
   ```
   ?debug=true
   ```

Reporting Issues
----------------

When reporting issues to developers, include:

1. **Error messages**: Exact text of any error messages
2. **Provider and model**: Which AI provider and model you were using
3. **Request details**: Number of images, approximate prompt length
4. **Steps to reproduce**: Detailed steps to reproduce the issue
5. **Expected vs. actual behavior**: What you expected vs. what happened
6. **Screenshots**: Include screenshots of the error if applicable
7. **Logs**: Relevant sections from logs (with sensitive information redacted)

Submit issues through the project's issue tracker with the label "multimodal".