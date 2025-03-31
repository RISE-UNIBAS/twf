"""Task base functions. Functions to start, update, end, and fail tasks."""
import time
import traceback
import logging
from datetime import datetime

from django.utils import timezone
from celery import Task as CeleryTask

from twf.clients.simple_ai_clients import AiApiClient
from twf.models import Task, Project, User

logger = logging.getLogger(__name__)


class BaseTWFTask(CeleryTask):
    """Base task for all TWF Celery tasks."""
    
    # Standard descriptions for common task types
    TASK_DESCRIPTIONS = {
        # Document and structure tasks
        "extract_zip_export_task": "Extraction of Transkribus export files to create document and page structures.",
        "create_collection": "Creation of a new collection in the project.",
        
        # AI collection processing tasks
        "search_openai_for_collection": "OpenAI processing of collection items for content extraction or enhancement.",
        "search_gemini_for_collection": "Gemini AI processing of collection items for content extraction or enhancement.",
        "search_claude_for_collection": "Claude AI processing of collection items for content extraction or enhancement.",
        "search_mistral_for_collection": "Mistral AI processing of collection items for content extraction or enhancement.",
        
        # AI document processing tasks
        "search_openai_for_docs": "OpenAI processing of documents for content extraction or enhancement.",
        "search_gemini_for_docs": "Gemini AI processing of documents for content extraction or enhancement.",
        "search_claude_for_docs": "Claude AI processing of documents for content extraction or enhancement.",
        "search_mistral_for_docs": "Mistral AI processing of documents for content extraction or enhancement.",
        
        # AI project query tasks (including multimodal)
        "query_project_openai": "OpenAI query with selected documents and optional image content.",
        "query_project_gemini": "Google Gemini query with selected documents and optional image content.",
        "query_project_claude": "Claude query with selected documents (text-only).",
        "query_project_mistral": "Mistral query with selected documents (text-only).",
        
        # Export tasks
        "export_data_task": "Export of project data to various formats.",
        "export_to_zenodo_task": "Export of project data to Zenodo repository.",
    }

    def before_start(self, task_id, args, kwargs):
        """Initialize project and user before the task starts."""
        self.task_id = task_id
        self.get_project_and_user(args[0], args[1])
        self.task_params = kwargs
        self.task_start_time = time.time()
        self.start_datetime = timezone.now()
        
        # Task tracking
        self.total_items = None
        self.processed_items = 0
        self.successful_items = 0
        self.failed_items = 0
        self.skipped_items = 0
        
        # Get standard description for this task type
        task_description = self.TASK_DESCRIPTIONS.get(self.name, "")
        
        # Create a new task object in the database
        self.twf_task = Task.objects.create(
            celery_task_id=task_id,
            project=self.project,
            user=self.user,
            status="STARTED",
            title=f"Started: {self.name}",
            description=task_description,
            text=f"Task initiated at {self.start_datetime.strftime('%Y-%m-%d %H:%M:%S')}.\n"
        )
        
        logger.info(f"Starting task {self.name} (ID: {task_id}) for project {self.project.title}")
        self.update_state(state="STARTED", meta={"current": 0, "total": 100, "text": "Task started"})

    @staticmethod
    def validate_task_parameters(kwargs, required_params):
        """
        Ensure all required parameters are present in kwargs.
        
        This method checks that all parameters in the required_params list are
        present in the kwargs dictionary. If any are missing, it raises a ValueError
        with a message indicating which parameters are missing.
        
        Args:
            kwargs (dict): Dictionary of keyword arguments to check
            required_params (list): List of parameter names that must be present
            
        Raises:
            ValueError: If any required parameters are missing from kwargs
        """
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

    def get_project_and_user(self, project_id, user_id):
        """
        Fetch project and user from the database and store them as instance attributes.
        
        This method is typically called during task initialization to retrieve the
        Project and User objects associated with the task. The objects are stored as
        instance attributes for use by other methods.
        
        Args:
            project_id (int): ID of the project to retrieve
            user_id (int): ID of the user to retrieve
            
        Raises:
            ValueError: If either project_id or user_id is missing, or if the
                       corresponding Project or User object does not exist
            
        Note:
            After successful execution, self.project and self.user will be set
            to the retrieved objects.
        """
        if not project_id or not user_id:
            raise ValueError("Project ID and User ID are required")

        try:
            self.project = Project.objects.get(pk=project_id)
            self.user = User.objects.get(pk=user_id)
        except Project.DoesNotExist:
            raise ValueError(f"Project with ID {project_id} not found")
        except User.DoesNotExist:
            raise ValueError(f"User with ID {user_id} not found")

    def set_total_items(self, total):
        """Set the total number of items for progress calculation."""
        self.total_items = total
        self.processed_items = 0  # Reset counter
        
        # Update task title to reflect the total
        if self.twf_task and total > 0:
            item_type = self.get_item_type_name()
            self.twf_task.title = f"Processing {total} {item_type}"
            self.twf_task.text += f"Found {total} {item_type} to process.\n"
            self.twf_task.save(update_fields=["title", "text"])
            logger.info(f"Task {self.task_id}: set to process {total} {item_type}")
    
    def get_item_type_name(self):
        """Return a descriptive name for the type of items being processed.
        Subclasses can override this if needed."""
        if "collection" in self.name.lower():
            return "collection items"
        elif "document" in self.name.lower() or "doc" in self.name.lower():
            return "documents"
        elif "page" in self.name.lower():
            return "pages"
        elif "dict" in self.name.lower():
            return "dictionary entries"
        elif "export" in self.name.lower():
            return "items"
        else:
            return "items"

    def advance_task(self, text="In progress", status="success"):
        """Increment the progress counter and update task progress.
        status can be 'success', 'failure', or 'skipped'
        """
        if self.total_items is not None and self.total_items > 0:
            self.processed_items += 1  # Increment processed count
            
            # Track detailed status
            if status.lower() == "success":
                self.successful_items += 1
            elif status.lower() == "failure":
                self.failed_items += 1
            elif status.lower() == "skipped":
                self.skipped_items += 1
                
            progress = int((self.processed_items / self.total_items) * 100)
            
            # Add detailed progress info to text
            detailed_text = f"{text} ({self.processed_items}/{self.total_items})"
            self.update_progress(progress, detailed_text)
            
            # Update text in database with more detail if appropriate
            if self.processed_items % 10 == 0 or self.processed_items == self.total_items:
                if self.twf_task:
                    elapsed = time.time() - self.task_start_time
                    avg_time = elapsed / self.processed_items if self.processed_items > 0 else 0
                    self.twf_task.text += f"Progress: {self.processed_items}/{self.total_items} items processed "
                    self.twf_task.text += f"({elapsed:.1f}s elapsed, {avg_time:.2f}s per item).\n"
                    self.twf_task.save(update_fields=["text"])

    def update_progress(self, progress, text="In progress"):
        """Update task progress in the database."""
        if self.twf_task:
            self.update_state(state="PROGRESS", meta={"current": progress, "total": 100, "text": text})
            self.twf_task.progress = progress
            
            # Update the title to reflect progress
            if progress < 100:
                item_type = self.get_item_type_name()
                if self.total_items:
                    self.twf_task.title = f"Processing {self.processed_items}/{self.total_items} {item_type} ({progress}%)"
            
            self.twf_task.save(update_fields=["progress", "title"])

    def process_ai_request(self, items, client_name, prompt, role_description, metadata_field):
        """Generalized function to process AI requests for multiple items."""
        # Set up the task with detailed tracking information
        total_items = len(items)
        self.set_total_items(total_items)
        
        # Configure AI client and update task description
        self.create_configured_client(client_name, role_description)
        
        if self.twf_task:
            self.twf_task.text += f"AI Client: {client_name.upper()}\n"
            self.twf_task.text += f"Model: {self.credentials['default_model']}\n"
            self.twf_task.text += f"Role: {role_description[:100]}...\n" if len(role_description) > 100 else f"Role: {role_description}\n"
            self.twf_task.text += f"Prompt: {prompt[:100]}...\n" if len(prompt) > 100 else f"Prompt: {prompt}\n"
            self.twf_task.save(update_fields=["text"])
        
        # Track success, failure, and timing stats
        successful_items = 0
        failed_items = 0
        total_time = 0
        
        # Process each item
        for item in items:
            try:
                start_time = time.time()
                response_dict, elapsed_time = self.prompt_client(item, prompt)
                
                # Save the AI response to the item's metadata
                item.metadata[metadata_field] = response_dict
                item.save(current_user=self.user)
                
                # Update task statistics
                successful_items += 1
                total_time += elapsed_time
                
                # Detailed progress message including timing information
                progress_msg = (f"Processed item {self.processed_items+1}/{total_items} "
                               f"in {elapsed_time:.2f}s")
                
                self.advance_task(text=progress_msg, status="success")
                
            except Exception as e:
                failed_items += 1
                error_msg = str(e)
                logger.error(f"Error processing item with {client_name}: {error_msg}")
                self.advance_task(
                    text=f"Error processing item {self.processed_items+1}/{total_items}",
                    status="failure"
                )
        
        # Update task with overall summary
        avg_time = total_time / successful_items if successful_items else 0
        
        # End task with detailed statistics
        self.end_task(
            status="SUCCESS",
            client_name=client_name,
            model=self.credentials['default_model'],
            total_time=total_time,
            average_time=avg_time,
            failed_items=failed_items
        )

    def process_single_ai_request(self, items, client_name, prompt, role_description, metadata_field, prompt_mode="text_only"):
        """
        Process an AI request with possible multimodal content (text + images).
        
        This method handles sending requests to various AI providers (OpenAI, Google Gemini,
        Anthropic Claude, Mistral) with optional multimodal content. It supports three modes:
        
        1. Text Only: Only sends the text prompt and context
        2. Images Only: Sends only images with a minimal text prompt
        3. Text + Images: Sends both text and images
        
        For image-based modes, the method automatically selects up to 5 images per document 
        from the provided items. Images are retrieved directly from the Transkribus server
        using their URLs rather than downloading them locally first.
        
        Args:
            items (QuerySet): The document items to process. These should have a get_text() method
                             and, for documents, should have associated pages with images.
            client_name (str): The name of the AI client to use: 'openai', 'genai', 'anthropic', or 'mistral'.
                              Note that only 'openai' and 'genai' currently support multimodal content.
            prompt (str): The prompt text from the user
            role_description (str): System role description for the AI model
            metadata_field (str): Field name for storing results in metadata
            prompt_mode (str): One of "text_only", "images_only", or "text_and_images".
                              Defaults to "text_only".
        
        Note:
            If a client doesn't support images but an image mode is requested, the method
            will automatically fall back to text-only mode with an appropriate warning.
        """
        self.set_total_items(1)
        self.create_configured_client(client_name, role_description)

        # Log the prompt mode
        self.twf_task.text += f"Prompt mode: {prompt_mode}\n"
        
        # Check if this client supports images
        supports_images = client_name in ['openai', 'genai'] and hasattr(self.client, 'add_image_resource')
        
        # If mode involves images but client doesn't support them, warn and fall back to text
        if prompt_mode in ['images_only', 'text_and_images'] and not supports_images:
            fallback_message = f"Warning: {client_name} does not support images. Falling back to text-only mode.\n"
            self.twf_task.text += fallback_message
            prompt_mode = "text_only"
        
        # Process images if needed based on mode
        if prompt_mode in ['images_only', 'text_and_images'] and supports_images:
            # Collect up to 5 images from each document
            image_count = 0
            for item in items:
                if hasattr(item, 'pages'):  # Verify this is a document
                    # Get up to 5 pages from this document, ordered by page number
                    pages = item.pages.all().order_by('tk_page_number')[:5]
                    
                    for page in pages:
                        # Use our new method to get image URL with 50% scaling
                        img_url = page.get_image_url(scale_percent=50)
                        if img_url:
                            self.client.add_image_resource(img_url)
                            self.twf_task.text += f"Added image from page {page.tk_page_number} of document {item.title}\n"
                            image_count += 1

            
            if image_count > 0:
                self.twf_task.text += f"Included {image_count} images in the prompt.\n"
            else:
                self.twf_task.text += "No valid images found in the selected documents.\n"
                
                # If we're in images-only mode but found no images, warn user and fall back to text
                if prompt_mode == 'images_only':
                    self.twf_task.text += "Warning: No images found but 'Images only' mode selected. Including text context instead.\n"
                    prompt_mode = "text_only"

        # Prepare the prompt text based on mode
        full_prompt = prompt
        
        # Add text context if mode includes text or if we're fallback from images-only with no images
        if prompt_mode in ['text_only', 'text_and_images']:
            context_text = ""
            for item in items:
                context_text += item.get_text() + "\n"
            
            # Only add context if it's not empty
            if context_text.strip():
                full_prompt += "\n\n" + "Context:\n" + context_text
        
        # For images-only mode with no text prompt, use a minimal prompt
        if prompt_mode == 'images_only':
            # If user provided a prompt, use it; otherwise use a default
            if not prompt.strip():
                full_prompt = "Please describe what you see in these images."
            
            # Images-only should NOT include text context
            self.twf_task.text += "Images-only mode: Using only images without text context.\n"
        
        # Call the API
        response, elapsed_time = self.client.prompt(model=self.credentials['default_model'],
                                                   prompt=full_prompt)
        response_dict = response.to_dict()

        # Clear image resources from client after use
        if hasattr(self.client, 'clear_image_resources'):
            self.client.clear_image_resources()

        self.end_task(ai_result=response_dict)

    def end_task(self, status="SUCCESS", error_msg=None, **kwargs):
        """Mark the task as completed or failed with detailed documentation."""
        if self.twf_task:
            # Calculate task duration
            end_time = timezone.now()
            duration = (end_time - self.start_datetime).total_seconds()
            
            # Format summary for the task text
            summary = self._generate_task_summary(status, duration, error_msg)
            self.twf_task.text += summary
            
            # Update the final task title with a concise summary
            item_type = self.get_item_type_name()
            if status == "SUCCESS":
                if self.total_items:
                    self.twf_task.title = f"Processed {self.processed_items} {item_type}"
                    if self.successful_items < self.processed_items:
                        self.twf_task.title += f" ({self.successful_items} successful)"
                else:
                    self.twf_task.title = f"Successfully completed {self.name}"
            else:
                if error_msg:
                    self.twf_task.title = f"Failed: {error_msg[:50]}..." if len(error_msg) > 50 else f"Failed: {error_msg}"
                else:
                    self.twf_task.title = f"Failed to process {item_type}"
            
            # Update metadata
            meta = {'current': 100, 'total': 100, 'text': 'Task finished'}
            meta['duration'] = duration
            meta['processed_items'] = self.processed_items
            meta['successful_items'] = self.successful_items
            meta['failed_items'] = self.failed_items
            meta['skipped_items'] = self.skipped_items
            
            if kwargs:
                meta.update(kwargs)
            
            # Update task state
            self.update_state(state=status, meta=meta)
            
            # Update database record
            self.twf_task.end_time = end_time
            self.twf_task.status = status
            self.twf_task.meta = meta
            self.twf_task.save(update_fields=["title", "text", "end_time", "status", "meta"])
            
            # Log completion
            log_msg = f"Task {self.name} (ID: {self.task_id}) completed with status {status}"
            if status == "SUCCESS":
                logger.info(log_msg)
            else:
                logger.error(f"{log_msg}: {error_msg}")
    
    def _generate_task_summary(self, status, duration, error_msg=None):
        """Generate a detailed summary of the task for documentation purposes."""
        summary = f"\n---- TASK SUMMARY ----\n"
        summary += f"Status: {status}\n"
        summary += f"Duration: {duration:.2f} seconds"
        
        if duration > 60:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            summary += f" ({minutes}m {seconds}s)"
        summary += "\n"
        
        if self.total_items:
            summary += f"Total items: {self.total_items}\n"
            summary += f"Processed items: {self.processed_items}\n"
            
            if self.successful_items > 0:
                summary += f"Successfully processed: {self.successful_items}\n"
            if self.failed_items > 0:
                summary += f"Failed to process: {self.failed_items}\n"
            if self.skipped_items > 0:
                summary += f"Skipped items: {self.skipped_items}\n"
                
            if self.processed_items > 0:
                avg_time = duration / self.processed_items
                summary += f"Average processing time per item: {avg_time:.2f} seconds\n"
        
        if error_msg:
            summary += f"\nError: {error_msg}\n"
            
        summary += "----------------------\n"
        return summary

    def create_configured_client(self, client_name, role_description):
        """
        Create and configure an AI client for the specified provider.
        
        This method handles the initialization of an AI client by retrieving the
        appropriate credentials from the project configuration and creating a new
        instance of AiApiClient. The client is configured with the specified
        provider, API key, and role description.
        
        Args:
            client_name (str): The name of the AI provider to use
                              ('openai', 'genai', 'anthropic', or 'mistral')
            role_description (str): System role description for the AI model
            
        Note:
            The created client is stored in self.client and can be used by other
            methods to interact with the AI provider.
        """
        self.client_name = client_name
        self.credentials = self.project.get_credentials(client_name)
        self.client = AiApiClient(api=client_name,
                                  api_key=self.credentials['api_key'],
                                  gpt_role_description=role_description)

    def prompt_client(self, item, prompt):
        """
        Send a prompt to the AI model with context from a specific item.
        
        This is a helper method that constructs a prompt with context from a single
        item (like a document or collection item) and sends it to the currently
        configured AI client. The item's text content is appended to the prompt
        as context.
        
        Note that this method does not handle images - for multimodal prompts,
        use process_single_ai_request with an appropriate prompt_mode.
        
        Args:
            item: An item with a get_text() method (Document, CollectionItem, etc.)
            prompt (str): The text prompt to send to the model
            
        Returns:
            tuple: (response_dict, elapsed_time) containing the parsed response
                  from the AI model and the time taken to receive it
        """
        context = item.get_text()
        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = self.client.prompt(model=self.credentials['default_model'],
                                                    prompt=prompt)
        response_dict = response.to_dict()
        return response_dict, elapsed_time
