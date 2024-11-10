Tags
====

The **Tags** section is designed to help users manage and organize tags extracted from page data. Tags are
categorized by types and can be used to group mentions into dictionary entries, which represent consistent
concepts or entities across the dataset. For example, variations in a place name like 'Lndn' and 'London'
can be grouped into a single dictionary entry. Each tag also keeps a reference to the page it was originally
found on, aiding in contextual analysis.

Sections
--------

Data
^^^^

- **Overview**: Displays a summary of the tag data, including the number of tag types, total tags, and the
  percentage of tags that have been grouped. This section provides a quick insight into the current status
  of tag organization.

- **All Tags**: Shows a list of all tags across the project, allowing users to view and manage individual
  tags and associated metadata.

- **Settings**: Contains configuration options related to tag extraction, grouping, and management, allowing
  users to customize tag processing workflows.

Tag Extraction
^^^^^^^^^^^^^^
The **Extract Tags** option initiates the tag extraction process, pulling tags from the text data associated
with the project's pages. This process identifies entities and other elements based on predefined tag types
or criteria.

Tag Workflows
^^^^^^^^^^^^^

- **Grouping Wizard**: Assists users in grouping similar or identical tags into dictionary entries, which
  helps create a standardized representation of entities within the project. This feature is useful for
  consolidating variations in tag spellings or formats.

- **Date Normalization**: Enables the normalization of dates across tags, making it easier to maintain
  consistency in date formats and ensuring that date-related tags can be accurately grouped and analyzed.

Tag Views
^^^^^^^^^

- **Open Tags**: Displays tags that are yet to be grouped or resolved. This view helps users track tags that
  require further action.

- **Parked Tags**: Lists tags that have been set aside for later review. Parked tags are not actively grouped
  but remain available for potential future categorization.

- **Resolved Tags**: Shows tags that have been successfully grouped or otherwise processed. Resolved tags
  represent completed entries within the tag management workflow.

- **Ignored Tags**: Contains tags marked as irrelevant or unnecessary, which have been excluded from the
  grouping and analysis process.

Tags Overview
-------------

**Tag Grouping Status**: Provides a detailed breakdown of each tag type, showing statistics such as:

- **Variation Type**: Name of the tag category, such as "mentioned_person" or "place."
- **Total Count**: Number of occurrences of this tag type in the project.
- **Percentage**: The proportion of this tag type relative to the total tag count.
- **Grouped**: Number of tags successfully grouped under each type.
- **Grouped %**: Percentage of tags grouped for each type.
- **Parked**: Number of tags that are parked for future grouping.
- **Parked %**: Percentage of tags parked for each type.
- **Unresolved**: Number of tags that have not yet been grouped or resolved.
- **Unresolved %**: Percentage of unresolved tags for each type, highlighting areas that may need further
  review.

This grouping status overview aids users in assessing the progress of tag organization, identifying tag
types with unresolved entries, and determining which areas may need additional attention for consistent data
representation.
