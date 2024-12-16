Transkribus workflow
====================
![pylint score](https://mperlet.github.io/pybadge/badges/9.30.svg)

# Table of Contents
1. [Navigation (Parts of the App)](#twf-navigation)
2. [Next Tasks](#next-tasks)

# TWF Navigation

## 1. Home
1. **Home** (Main dashboard or entry point)
2. **About** (Information about the app or organization)

### User Options
3. **Overview**
4. **User Profile**
5. **Change Password**
6. **User Management**
7. **Logout**
8. **Admin**

---

## 2. Project
1. **Overview** (Project details or summary)
2. **Task Monitor** (Monitor ongoing tasks)
3. **Saved Prompts** (Manage or view saved prompts)

### Settings
4. **General Settings** (Configure general project settings)
5. **Credential Settings** (Manage project-specific credentials)
6. **Task Settings** (Configure task-specific settings)
7. **Export Settings** (Settings for exporting data)

### Setup Project
8. **Request Transkribus Export** (Initiate a Transkribus export)
9. **Test Export** (Run test exports)
10. **Extract Transkribus Export** (Extract data from Transkribus)
11. **Create Copy of Project** (Duplicate a project)

### Ask Questions
12. **Query** (Perform manual queries)
13. **Ask ChatGPT** (AI-based assistance for project tasks)

---

## 3. Documents
### Your Documents
1. **Overview** (General summary or statistics)
2. **Browse Documents** (View and manage documents)

### Document Batch
3. **ChatGPT** (Batch processing using ChatGPT)
4. **Gemini** (Batch processing using Gemini)
5. **Claude** (Batch processing using Claude)

### Create Documents
6. **Manual Document Creation** (Add documents manually)

---

## 4. Tags
### Data
1. **Overview** (Summary or statistics for tags)
2. **All Tags** (View and manage tags)
3. **Settings** (Configure tag-related settings)

### Tag Extraction
4. **Extract Tags** (Extract tags from data)

### Tag Workflows
5. **Grouping Wizard** (Organize tags into groups)
6. **Date Normalization** (Normalize date-related tags)

### Tag Views
7. **Open Tags** (Pending or in-progress tags)
8. **Parked Tags** (Tags on hold)
9. **Resolved Tags** (Completed tags)
10. **Ignored Tags** (Excluded tags)

---

## 5. Metadata
### Metadata Overview
1. **Overview** (Summary and statistics for metadata)

### Load Metadata
2. **Load JSON Metadata** (Import metadata from JSON files)
3. **Load Google Sheets Metadata** (Import metadata from Google Sheets)

### Metadata Workflows
4. **Extract Controlled Values** (Extract controlled vocabulary values)
5. **Review Document Metadata** (Analyze/edit document metadata)
6. **Review Page Metadata** (Analyze/edit page metadata)

---

## 6. Dictionaries
### Dictionaries Options
1. **Overview** (General summary or statistics)
2. **Dictionaries** (View/manage dictionaries)
3. **Add Dictionaries** (Import dictionaries)
4. **Create New Dictionary** (Create a dictionary from scratch)

### Automated Workflows
5. **GND** (Automated dictionary enrichment with GND data)
6. **Wikidata** (Automated workflows with Wikidata)
7. **Geonames** (Automated workflows with Geonames)
8. **Open AI** (AI-based workflows)

### Supervised Workflows
9. **GND** (Supervised workflows with GND)
10. **Wikidata** (Supervised workflows with Wikidata)
11. **Geonames** (Supervised workflows with Geonames)
12. **Open AI** (Supervised AI workflows)

### Manual Workflows
13. **Manual Assignment** (Manually assign dictionary entries)
14. **Merge Entries** (Merge duplicate or related entries)

---

## 7. Collections
1. **Overview** (Summary or statistics for collections)
2. **Create New Collection** (Add a new collection)
3. **Your Collections** (View/manage collections)

---

## 8. Import/Export
### Overview
1. **Export Overview** (Summary/statistics for exports)

### Import Data
2. **Import Dictionaries** (Import dictionaries)

### Export Data
3. **Export Documents** (Export document data)
4. **Export Collections** (Export collection data)
5. **Export Dictionaries** (Export dictionary data)
6. **Export Tags** (Export tag data)

### Export Project
7. **Export Project** (Export the entire project)


# Next Tasks

| ID   | Section       | Task Description                                                                             | Priority       |
|------|---------------|-----------------------------------------------------------------------------------------------|----------------|
| M-01 | Metadata      | Implement "3 numbers" in Overview                                                             | ![Low](https://img.shields.io/badge/Priority-Low-lightgrey) |
| M-02 | Metadata      | Implement functionality to load JSON metadata                                                 | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| M-03 | Metadata      | Review Document Metadata / Review Page Metadata: Reimplement workflows and document settings  | ![High](https://img.shields.io/badge/Priority-High-red) |
| P-01 | Project       | Implement functionality to duplicate the project                                              | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| C-01 | Collections   | Implement "3 numbers" in Overview                                                             | ![Low](https://img.shields.io/badge/Priority-Low-lightgrey) |
| C-02 | Collections   | Remove differing navigation structure "Your collection"; create browse page instead           | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| IE-01| Import/Export | Implement "3 numbers" in Overview                                                             | ![Low](https://img.shields.io/badge/Priority-Low-lightgrey) |
| IE-02| Import/Export | Redo form and check import for Import Dictionaries; show import file structure                | ![High](https://img.shields.io/badge/Priority-High-red) |
| IE-03| Import/Export | Implement Export Documents                                                                    | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| IE-04| Import/Export | Implement Export Collections                                                                  | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| IE-05| Import/Export | Add number of items in dictionaries to Export Dictionaries                                    | ![Low](https://img.shields.io/badge/Priority-Low-lightgrey) |
| IE-06| Import/Export | Add tag type and tag origin to Export Tags                                                    | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| IE-07| Import/Export | Implement function for Export Project                                                         | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| D-01 | Dictionaries  | Fix bug and finish implementation for Norm Data Wizard                                        | ![High](https://img.shields.io/badge/Priority-High-red) |
| D-02 | Dictionaries  | **Automated Workflows**: Fix GND bug `kombu.exceptions.EncodeError: Project not JSON serializable` | ![High](https://img.shields.io/badge/Priority-High-red) |
| D-03 | Dictionaries  | **Automated Workflows**: Finish implementation for Wikidata                                  | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| D-04 | Dictionaries  | **Automated Workflows**: Finish implementation for Geonames                                  | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| D-05 | Dictionaries  | **Automated Workflows**: Finish implementation for OpenAI; add prompt-saving and recalling   | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| H-01 | Home          | Add view and form for User Options to change username, ORCID, real name, and email address    | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
| G-01 | General       | Implement user roles for access control to settings, etc.                                    | ![Low](https://img.shields.io/badge/Priority-Low-lightgrey) |
| G-02 | General       | Create User Tasks to assign to users                                                          | ![Low](https://img.shields.io/badge/Priority-Low-lightgrey) |
| G-03 | General       | Implement modal dialog to confirm actions                                                    | ![Medium](https://img.shields.io/badge/Priority-Medium-orange) |
