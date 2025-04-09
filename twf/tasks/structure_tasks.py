"""Celery tasks for extracting Transkribus export files."""
import logging
import os
import time
import uuid
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from celery import shared_task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from simple_alto_parser import PageFileParser

from twf.models import Document, Page
from twf.utils.page_file_meta_data_reader import extract_transkribus_file_metadata
from twf.tasks.task_base import BaseTWFTask
from twf.utils.file_utils import delete_all_in_folder

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTWFTask)
def extract_zip_export_task(self, project_id, user_id, **kwargs):
    """Extract the Transkribus export zip file and create Document and Page instances."""
    extracted_files = 0
    created_documents = 0
    created_pages = 0
    
    try:
        # Step 1: Validate and prepare the zip file
        zip_file, extract_to_path = prepare_zip_file(self.project, self)
        if self.twf_task:
            self.twf_task.text += f"Prepared zip file: {zip_file.name}\n" 
            self.twf_task.text += f"Extraction path: {extract_to_path}\n"
            self.twf_task.save(update_fields=["text"])

        # Step 2: Extract files from the zip archive
        copied_files = extract_files_from_zip(zip_file, extract_to_path, self.project, self)
        extracted_files = len(copied_files)
        if self.twf_task:
            self.twf_task.text += f"Extracted {extracted_files} files from the zip archive.\n"
            self.twf_task.save(update_fields=["text"])

        # Step 3: Process extracted files and create/update Document and Page instances
        doc_count, page_count = process_extracted_files(copied_files, self.project, self.user, self)
        created_documents = doc_count
        created_pages = page_count
        if self.twf_task:
            self.twf_task.text += f"Created/updated {doc_count} documents and {page_count} pages.\n"
            self.twf_task.save(update_fields=["text"])

        # Step 4: Parse page data
        parse_pages(self.project, self.user, self)

        # Finalize the task with detailed information
        self.end_task(
            status="SUCCESS",
            extracted_files=extracted_files,
            created_documents=created_documents,
            created_pages=created_pages
        )

        return {
            'status': 'completed',
            'extracted_files': extracted_files,
            'created_documents': created_documents,
            'created_pages': created_pages
        }

    except Exception as e:
        # Log the error and end the task with failure status
        error_msg = str(e)
        logger.error(f"Error in extract_zip_export_task: {error_msg}")
        self.end_task(
            status="FAILURE", 
            error_msg=error_msg,
            extracted_files=extracted_files,
            created_documents=created_documents,
            created_pages=created_pages
        )
        raise


def prepare_zip_file(project, celery_task):
    """Check the zip file and prepare the extraction path."""
    zip_file = project.downloaded_zip_file
    if not zip_file or not os.path.exists(zip_file.path):
        error_message = "The zip file does not exist in the file system."
        raise ValueError(error_message)

    fs = FileSystemStorage()
    extract_to_path = fs.path(f"transkribus_exports/{project.collection_id}/")
    if not fs.exists(extract_to_path):
        os.makedirs(extract_to_path)
    delete_all_in_folder(extract_to_path)

    celery_task.update_progress(2)
    return zip_file, extract_to_path


def extract_files_from_zip(zip_file, extract_to_path, project, celery_task):
    """Extract valid files from the zip archive."""
    copied_files = []
    with zipfile.ZipFile(zip_file.path, 'r') as zip_ref:
        valid_files = [
            x for x in zip_ref.infolist()
            if ("/page/" in x.filename and x.filename.endswith(".xml"))
            or x.filename.endswith('metadata.xml') or x.filename.endswith('mets.xml')
        ]
        total_files = len(valid_files)

        for i, file_info in enumerate(valid_files, start=1):
            with zip_ref.open(file_info) as file_data:
                new_filename = generate_new_filename(file_info, project)
                new_filepath = Path(extract_to_path) / new_filename
                with open(new_filepath, 'wb') as new_file:
                    new_file.write(file_data.read())
                    copied_files.append(new_filepath)

                # Update progress with detailed description
                progress = (i / total_files) * 30  # Allocate 30% for extraction
                celery_task.update_progress(
                    2 + progress,
                    text=f"Extracting file {i}/{total_files}: {file_info.filename}"
                )
    return copied_files


def generate_new_filename(file_info, project):
    """Generate a new filename for extracted files."""
    if file_info.filename.endswith(('metadata.xml', 'mets.xml')):
        return f"{file_info.filename.split('/')[0]}_{file_info.filename.split('/')[-1]}"
    else:
        return f"{project.collection_id}_{uuid.uuid4().hex}.xml"


def process_extracted_files(copied_files, project, extracting_user, celery_task):
    """Process extracted files and create/update Document and Page instances.
    
    Returns:
        tuple: (document_count, page_count) The number of documents and pages created/updated
    """
    all_existing_documents = set(Document.objects.filter(project=project).values_list('document_id', flat=True))
    total_files = len(copied_files)
    
    # Track document and page creation
    processed_documents = set()
    processed_pages = 0
    failed_files = 0
    
    # Separate regular XML files from metadata files
    page_xml_files = []
    metadata_files = []
    
    for file in copied_files:
        file_str = str(file)
        if file_str.endswith(('metadata.xml', 'mets.xml')):
            metadata_files.append(file)
        else:
            page_xml_files.append(file)
    
    # Log metadata files found
    if celery_task.twf_task:
        celery_task.twf_task.text += f"Found {len(metadata_files)} metadata files and {len(page_xml_files)} page files.\n"
        celery_task.twf_task.save(update_fields=["text"])
    
    # Process page XML files
    for i, file in enumerate(page_xml_files, start=1):
        try:
            data = extract_transkribus_file_metadata(file)
            doc_id, is_new_page = handle_document_and_page(
                data, file, project, extracting_user, all_existing_documents, metadata_files
            )
            
            # Track the processed document
            processed_documents.add(doc_id)
            
            # Count new pages
            if is_new_page:
                processed_pages += 1
                
            # Add more details about the document and page being processed
            celery_task.advance_task(
                text=f"Processed file {i}/{len(page_xml_files)}: Created/updated document {doc_id} with page {data['pageId']}", 
                status="success"
            )
        except Exception as e:
            error_msg = f"Failed to process file {file}: {e}"
            logging.warning(error_msg)
            failed_files += 1
            file_name = os.path.basename(str(file))
            celery_task.advance_task(
                text=f"Error processing file {i}/{len(page_xml_files)}: {file_name} - {str(e)[:100]}", 
                status="failure"
            )
        
        # Update progress with detailed information about the file being processed
        file_name = os.path.basename(str(file))
        progress = (i / total_files) * 30  # Allocate another 30% for processing
        celery_task.update_progress(
            32 + progress,
            text=f"Processing file {i}/{total_files}: {file_name}"
        )
    
    # Add summary to task text
    if celery_task.twf_task:
        celery_task.twf_task.text += f"\nSummary of document processing:\n"
        celery_task.twf_task.text += f"- Documents processed: {len(processed_documents)}\n"
        celery_task.twf_task.text += f"- Pages created: {processed_pages}\n"
        celery_task.twf_task.text += f"- Failed files: {failed_files}\n"
        celery_task.twf_task.save(update_fields=["text"])
    
    return len(processed_documents), processed_pages


def parse_metadata_files(files, doc_id):
    """Extract metadata from metadata.xml and mets.xml files for a document.
    
    Args:
        files: List of file paths
        doc_id: Document ID to find matching metadata files
    
    Returns:
        dict: Metadata extracted from the files
    """
    metadata = {}
    
    # Look for matching metadata files
    metadata_file = None
    mets_file = None
    
    for file in files:
        file_str = str(file)
        file_basename = os.path.basename(file_str)
        
        # Check if the filename contains the document ID
        if doc_id in file_str:
            if file_str.endswith('metadata.xml'):
                metadata_file = file
            elif file_str.endswith('mets.xml'):
                mets_file = file
    
    # Extract metadata from metadata.xml
    if metadata_file:
        try:
            tree = ET.parse(metadata_file)
            root = tree.getroot()
            
            # Extract basic metadata
            title_elem = root.find(".//title")
            if title_elem is not None and title_elem.text:
                metadata['title'] = title_elem.text.strip()
            
            author_elem = root.find(".//author")
            if author_elem is not None and author_elem.text:
                metadata['author'] = author_elem.text.strip()
                
            # Try to extract more fields
            for field in ['writer', 'description', 'language', 'authority', 'external_id']:
                elem = root.find(f".//{field}")
                if elem is not None and elem.text:
                    metadata[field] = elem.text.strip()
            
            # Add all other available fields
            for elem in root.findall(".//*"):
                if elem.text and elem.text.strip() and elem.tag not in metadata:
                    metadata[elem.tag] = elem.text.strip()
        except Exception as e:
            logging.warning(f"Error parsing metadata file for document {doc_id}: {e}")
    
    # Extract additional metadata from mets.xml
    if mets_file:
        try:
            tree = ET.parse(mets_file)
            root = tree.getroot()
            
            # Extract metadata from mets file (often has more detailed info)
            for elem in root.findall(".//*"):
                if elem.text and elem.text.strip() and elem.tag not in metadata:
                    # Convert namespace prefixed tags to plain tag names
                    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    metadata[tag] = elem.text.strip()
        except Exception as e:
            logging.warning(f"Error parsing mets file for document {doc_id}: {e}")
    
    return metadata


def handle_document_and_page(data, file, project, extracting_user, existing_documents, metadata_files=None):
    """Handle creation/updating of Document and Page instances.
    
    Args:
        data: Page metadata
        file: XML file path
        project: Project instance
        extracting_user: User performing the extraction
        existing_documents: Set of existing document IDs
        metadata_files: List of all XML files (for metadata extraction)
    
    Returns:
        tuple: (document_id, is_new_page) The document ID and whether a new page was created
    """
    doc_instance, doc_created = Document.objects.get_or_create(
        project=project,
        document_id=data['docId'],
        defaults={'created_by': extracting_user, 'modified_by': extracting_user}
    )
    existing_documents.discard(doc_instance.document_id)
    
    # Extract and update document metadata if we have metadata files
    if metadata_files:
        document_metadata = parse_metadata_files(metadata_files, data['docId'])
        
        # Update document metadata
        if document_metadata:
            # Set document title if available
            if 'title' in document_metadata and not doc_instance.title:
                doc_instance.title = document_metadata['title']
            
            # Update document metadata field if it exists
            if hasattr(doc_instance, 'metadata'):
                # Merge with existing metadata but wrap in "transkribus" key
                existing_metadata = doc_instance.metadata or {}
                
                # Create or update the "transkribus" key
                if 'transkribus' not in existing_metadata:
                    existing_metadata['transkribus'] = {}
                
                # Add all extracted metadata to the transkribus key
                existing_metadata['transkribus'].update(document_metadata)
                doc_instance.metadata = existing_metadata
            
            # Save document with updated metadata
            doc_instance.save(current_user=extracting_user)

    page_instance, page_created = Page.objects.get_or_create(
        document=doc_instance,
        tk_page_id=data['pageId'],
        tk_page_number=data['pageNr'],
        defaults={'created_by': extracting_user, 'modified_by': extracting_user}
    )
    # Properly assign the file to the FileField by opening and saving the file
    with open(file, 'rb') as f:
        file_name = os.path.basename(str(file))
        page_instance.xml_file.save(file_name, f, save=False)
    
    page_instance.save(current_user=extracting_user)
    
    return doc_instance.document_id, page_created


def parse_pages(project, extracting_user, celery_task):
    """Parse pages and extract data."""
    all_pages = Page.objects.filter(document__project=project).order_by('document__document_id', 'tk_page_number')
    total_pages = all_pages.count()
    
    # Set total items for progress tracking
    celery_task.set_total_items(total_pages)
    
    successfully_parsed = 0
    failed_parsing = 0
    
    for i, page in enumerate(all_pages, start=1):
        try:
            page_parser = PageFileParser(parser_config={
                'line_type': 'TextRegion',
                'logging': {'level': logging.WARN},
                'export': {'json': {'print_files': True, 'print_filename': True, 'print_file_meta_data': True}}
            })
            page_parser.add_file(page.xml_file.path)
            page_parser.parse()
            page.parsed_data = page_parser.get_alto_files()[0].get_standalone_json_object()
            page.last_parsed_at = timezone.now()
            page.save(current_user=extracting_user)
            
            successfully_parsed += 1
            celery_task.advance_task(
                text=f"Parsed page {i}/{total_pages}: Page {page.tk_page_id} (#{page.tk_page_number}) from document {page.document.document_id}",
                status="success"
            )
        except Exception as e:
            failed_parsing += 1
            error_msg = f"Failed to parse page {page.tk_page_id} from document {page.document.document_id}: {str(e)}"
            logger.error(error_msg)
            celery_task.advance_task(
                text=f"Error parsing page {i}/{total_pages}: Page {page.tk_page_id} (#{page.tk_page_number}) from document {page.document.document_id} - {str(e)[:100]}",
                status="failure"
            )
    
    # Add summary to task text
    if celery_task.twf_task:
        celery_task.twf_task.text += f"\nParsing summary:\n"
        celery_task.twf_task.text += f"- Successfully parsed: {successfully_parsed} pages\n"
        if failed_parsing > 0:
            celery_task.twf_task.text += f"- Failed to parse: {failed_parsing} pages\n"
        celery_task.twf_task.save(update_fields=["text"])


