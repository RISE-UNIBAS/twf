"""This module contains functions that are used to save the progress and details of a process to the cache."""
import time
from django.core.cache import cache


def add_details(text, project_id, job_name, separator='---'):
    """This function saves the details of a process to the cache."""
    current_details = cache.get(f'{project_id}_extract-tags-progress-detail', '')
    cache.set(f'{project_id}_{job_name}', current_details + text + separator)


def set_details(text, project_id, job_name):
    """This function saves the details of a process to the cache."""
    cache.set(f'{project_id}_{job_name}', text)


def calculate_and_set_progress(processed_steps, total_steps, project_id, job_name):
    """This function calculates the progress of a process and saves it to the cache."""
    progress = (processed_steps / total_steps) * 100
    set_progress(progress, project_id, job_name)


def set_progress(progress, project_id, job_name):
    """This function saves the progress of a process to the cache."""
    cache.set(f'{project_id}_{job_name}', progress)


def base_event_stream(project_id, job_name, sleep_time=1):
    """This function streams the progress of a process to the client."""

    while True:
        progress = cache.get(f'{project_id}_{job_name}', 0)
        yield f'data: {progress}\n\n'
        if progress >= 100:
            break
        time.sleep(sleep_time)


def base_detail_event_stream(project_id, job_name, sleep_time=1):
    """This function streams the details of a process to the client."""

    while True:
        details = cache.get(f'{project_id}_{job_name}', 'no details available')
        if details:
            yield f'data: {details}\n\n'
        if details == "FINISHED":
            yield 'event: complete\ndata: Process completed.\n\n'
            break
        set_details('', project_id, job_name)    # Clear after sending
        time.sleep(sleep_time)
