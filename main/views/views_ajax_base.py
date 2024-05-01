"""This module contains functions that are used to save the progress and details of a process to the cache."""
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
