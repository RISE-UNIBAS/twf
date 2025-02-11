import requests
from django.conf import settings


ZENODO_URL = "https://zenodo.org/api/deposit/depositions"
LICENSE_CHOICES = [
    ('CC BY 4.0', 'Creative Commons Attribution 4.0 International (CC BY 4.0)'),
    ('CC BY-SA 4.0', 'Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)'),
    ('CC0 1.0', 'Creative Commons Zero v1.0 Universal (CC0 1.0)'),
    ('MIT', 'MIT License'),
    ('GPL-3.0', 'GNU General Public License v3.0 (GPL-3.0)'),
    ('Apache-2.0', 'Apache License 2.0'),
]


def create_metadata_json(project):
    project_metadata = {
        "metadata":{
            "title": project.title,
            "upload_type": "dataset",
            "description": project.description,
            "creators": [
                {
                    "name": f"{project.owner.profile.last_name}, {project.owner.profile.first_name}",
                    "affiliation": project.owner.profile.affiliation
                }
            ]
        },
        "keywords": project.keywords,
        "license": project.license,
        "access_right": "open",
        "relations": {
            "version": project.version
        }
    }

    for member in project.members.all():
        project_metadata["metadata"]["creators"].append({
            "name": f"{member.user.last_name}, {member.user.first_name}",
            "affiliation": member.affiliation
        })
    return project_metadata

def create_project_md(project):
    project_md = f"""
# {project.title} Dataset

## Project Overview
**Title:** {project.title}
**Description:** {project.description}
**Version:** {project.version}
**Creator:** {project.owner.user.last_name}, {project.owner.user.first_name} ({project.owner.affiliation})
**Keywords:** {', '.join(project.keywords)}
**License:** {project.license}

## Members
"""
    for member in project.members.all():
        project_md += f"- {member.user.last_name}, {member.user.first_name} ({member.affiliation})\n"

    project_md += f"""
## Workflow Description
{project.workflow_description}

## Technical Details
The data stems from the Transkribus platform and has been processed by the TWF.

- **Data Format:** Tha data is stored as JSON files.
- **Data Structure:** The data is structured in documents and pages. Documents and pages contain additional metadata,
injected by the TWF.
- **Data Volume:** The dataset contains {project.documents.all().count()} documents.
- **Transkribus Collection ID:** {project.collection_id}
- **Transkribus Export Date:** {project.downloaded_at}
- **TWF Version:** {settings.TWF_VERSION} 
"""
    return project_md

def upload_to_zenodo(project):
    pass

def get_zenodo_uploads(project):
    """Returns a list of uploads to Zenodo."""
    access_token = project.get_credentials('zenodo').get('zenodo_token')

    r = requests.get(ZENODO_URL,
                     params={'access_token': access_token})

    if r.status_code != 200:
        return None

    return r.json()