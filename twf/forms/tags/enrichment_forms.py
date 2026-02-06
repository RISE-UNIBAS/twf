"""
Tag Enrichment Forms
===================

Forms for enriching tags with normalized data (dates, bible verses, locations, etc.).
"""

from django import forms
from django.urls import reverse
from abc import ABCMeta, abstractmethod
import re
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, HTML, ButtonHolder
from twf.models import TagEnrichment


class AbstractFormMeta(ABCMeta, type(forms.Form)):
    """Metaclass combining ABC and Django Form metaclass."""


class BaseTagEnrichmentForm(forms.Form, metaclass=AbstractFormMeta):
    """
    Abstract base for tag enrichment forms.

    Provides common structure for all enrichment types.
    Subclasses must implement:
    - propose_normalization(): Generate initial normalized value
    - build_enrichment_data(): Build structured JSON data
    - get_enrichment_type(): Return enrichment type string
    """

    tag_id = forms.IntegerField(widget=forms.HiddenInput())
    normalized_value = forms.CharField(
        max_length=500,
        label="Normalized Value",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, project=None, tag=None, **kwargs):
        if not project or not tag:
            raise ValueError("Project and tag are required.")

        super().__init__(*args, **kwargs)
        self.project = project
        self.tag = tag
        self.fields["tag_id"].initial = tag.pk

        # Get initial normalized proposal
        proposal = self.propose_normalization(tag.variation, project)
        self.fields["normalized_value"].initial = proposal

        # Setup crispy forms helper with buttons
        park_url = reverse("twf:tags_park", kwargs={"pk": tag.pk})
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "tag_id",
            self._get_form_fields_layout(),
            ButtonHolder(
                Submit(
                    "save_and_next",
                    "Save & Next",
                    css_class="btn btn-primary",
                ),
                HTML(
                    f'<a href="{park_url}" class="btn btn-secondary ms-2">'
                    f'<i class="fa fa-box-archive"></i> Park</a>'
                ),
                css_class="mt-3",
            ),
        )

    def _get_form_fields_layout(self):
        """
        Get layout for form-specific fields.

        Override in subclasses to customize field layout.
        Returns field names or Layout objects for crispy forms.
        """
        # Default: return all fields except tag_id
        return Div(
            *[
                field_name
                for field_name in self.fields.keys()
                if field_name != "tag_id"
            ]
        )

    @abstractmethod
    def propose_normalization(self, variation, project):
        """
        Generate initial normalization proposal.

        Parameters
        ----------
        variation : str
            The tag variation text
        project : Project
            The project context

        Returns
        -------
        str
            Proposed normalized value
        """

    @abstractmethod
    def build_enrichment_data(self, cleaned_data):
        """
        Build structured enrichment_data dict from form data.

        Parameters
        ----------
        cleaned_data : dict
            Form cleaned data

        Returns
        -------
        dict
            Structured data for enrichment_data JSONField
        """

    @abstractmethod
    def get_enrichment_type(self):
        """
        Return enrichment type string.

        Returns
        -------
        str
            Type identifier (e.g., 'date', 'verse', 'location')
        """

    def save(self, user):
        """
        Create TagEnrichment and link to tag.

        Parameters
        ----------
        user : User
            User performing the enrichment

        Returns
        -------
        TagEnrichment
            Created enrichment instance
        """
        enrichment = TagEnrichment(
            variation=self.tag.variation,
            enrichment_type=self.get_enrichment_type(),
            normalized_value=self.cleaned_data["normalized_value"],
            enrichment_data=self.build_enrichment_data(self.cleaned_data),
        )
        enrichment.save(current_user=user)

        self.tag.tag_enrichment_entry = enrichment
        self.tag.save(current_user=user)

        return enrichment


class DateEnrichmentForm(BaseTagEnrichmentForm):
    """Form for date normalization to EDTF format."""

    resolve_to = forms.ChoiceField(
        label="Resolve to",
        choices=[("year", "Year"), ("month", "Month"), ("day", "Day")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    input_date_format = forms.ChoiceField(
        label="Input Date Format",
        choices=[
            ("DMY", "Day-Month-Year"),
            ("MDY", "Month-Day-Year"),
            ("YMD", "Year-Month-Day"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get date config from project
        conf = self.project.get_task_configuration("date_normalization")
        self.fields["resolve_to"].initial = conf.get("resolve_to", "day")
        self.fields["input_date_format"].initial = conf.get("input_date_format", "DMY")

    def propose_normalization(self, variation, project):
        """
        Parse date string to EDTF format.

        Parameters
        ----------
        variation : str
            Date variation text
        project : Project
            Project context

        Returns
        -------
        str
            EDTF date string
        """
        from twf.utils.date_utils import parse_date_string

        conf = project.get_task_configuration("date_normalization")
        return parse_date_string(
            variation,
            resolve_to=conf.get("resolve_to", "day"),
            date_format=conf.get("input_date_format", "DMY"),
        )

    def build_enrichment_data(self, cleaned_data):
        """
        Build structured date data from EDTF.

        Parameters
        ----------
        cleaned_data : dict
            Form cleaned data

        Returns
        -------
        dict
            Date data with year, month, day, edtf fields
        """
        edtf = cleaned_data["normalized_value"]

        # Parse EDTF to structured data
        data = {"edtf": edtf}
        parts = edtf.split("-")
        if len(parts) >= 1 and parts[0].isdigit():
            data["year"] = int(parts[0])
        if len(parts) >= 2 and parts[1] not in ("XX", "xx") and parts[1].isdigit():
            data["month"] = int(parts[1])
        if len(parts) >= 3 and parts[2] not in ("XX", "xx") and parts[2].isdigit():
            data["day"] = int(parts[2])

        return data

    def get_enrichment_type(self):
        """Return enrichment type."""
        return "date"


class BibleVerseEnrichmentForm(BaseTagEnrichmentForm):
    """Form for bible verse normalization."""

    book = forms.CharField(
        max_length=100,
        label="Book",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="e.g., Hebrews, Genesis, Matthew",
    )

    chapter = forms.IntegerField(
        label="Chapter",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    verse = forms.IntegerField(
        label="Verse",
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        help_text="Leave empty for entire chapter",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parse variation to populate fields
        self._parse_and_populate()

    def propose_normalization(self, variation, project):
        """
        Attempt to parse bible verse notation.

        Parameters
        ----------
        variation : str
            Verse variation text
        project : Project
            Project context

        Returns
        -------
        str
            Normalized verse reference
        """
        # Pattern: "Hebr. 13. V. 7." or "Genesis 1:1"
        patterns = [
            r"(\w+)\.\s*(\d+)\.\s*V\.\s*(\d+)",  # "Hebr. 13. V. 7."
            r"(\w+)\s+(\d+):(\d+)",  # "Hebrews 13:7"
            r"(\w+)\s+(\d+),\s*(\d+)",  # "Hebrews 13, 7"
        ]

        for pattern in patterns:
            match = re.search(pattern, variation, re.IGNORECASE)
            if match:
                book_abbrev, chapter, verse = match.groups()
                book_full = self.expand_book_abbreviation(book_abbrev)
                if verse:
                    return f"{book_full} {chapter}:{verse}"
                return f"{book_full} {chapter}"

        return variation  # Return as-is if can't parse

    def _parse_and_populate(self):
        """Parse variation to populate form fields."""
        variation = self.tag.variation

        patterns = [
            r"(\w+)\.\s*(\d+)\.\s*V\.\s*(\d+)",  # "Hebr. 13. V. 7."
            r"(\w+)\s+(\d+):(\d+)",  # "Hebrews 13:7"
            r"(\w+)\s+(\d+),\s*(\d+)",  # "Hebrews 13, 7"
        ]

        for pattern in patterns:
            match = re.search(pattern, variation, re.IGNORECASE)
            if match:
                book_abbrev, chapter, verse = match.groups()
                book_full = self.expand_book_abbreviation(book_abbrev)
                self.fields["book"].initial = book_full
                self.fields["chapter"].initial = int(chapter)
                if verse:
                    self.fields["verse"].initial = int(verse)
                break

    def expand_book_abbreviation(self, abbrev):
        """
        Expand common bible book abbreviations.

        Parameters
        ----------
        abbrev : str
            Book abbreviation

        Returns
        -------
        str
            Full book name
        """
        abbrev_map = {
            "gen": "Genesis",
            "exod": "Exodus",
            "lev": "Leviticus",
            "num": "Numbers",
            "deut": "Deuteronomy",
            "josh": "Joshua",
            "judg": "Judges",
            "ruth": "Ruth",
            "sam": "Samuel",
            "kgs": "Kings",
            "chr": "Chronicles",
            "ezra": "Ezra",
            "neh": "Nehemiah",
            "esth": "Esther",
            "job": "Job",
            "ps": "Psalms",
            "prov": "Proverbs",
            "eccl": "Ecclesiastes",
            "song": "Song of Solomon",
            "isa": "Isaiah",
            "jer": "Jeremiah",
            "lam": "Lamentations",
            "ezek": "Ezekiel",
            "dan": "Daniel",
            "hos": "Hosea",
            "joel": "Joel",
            "amos": "Amos",
            "obad": "Obadiah",
            "jonah": "Jonah",
            "mic": "Micah",
            "nah": "Nahum",
            "hab": "Habakkuk",
            "zeph": "Zephaniah",
            "hag": "Haggai",
            "zech": "Zechariah",
            "mal": "Malachi",
            "matt": "Matthew",
            "mark": "Mark",
            "luke": "Luke",
            "john": "John",
            "acts": "Acts",
            "rom": "Romans",
            "cor": "Corinthians",
            "gal": "Galatians",
            "eph": "Ephesians",
            "phil": "Philippians",
            "col": "Colossians",
            "thess": "Thessalonians",
            "tim": "Timothy",
            "titus": "Titus",
            "philem": "Philemon",
            "hebr": "Hebrews",
            "jas": "James",
            "pet": "Peter",
            "jn": "John",
            "jude": "Jude",
            "rev": "Revelation",
        }
        return abbrev_map.get(abbrev.lower(), abbrev.title())

    def build_enrichment_data(self, cleaned_data):
        """
        Build structured verse data.

        Parameters
        ----------
        cleaned_data : dict
            Form cleaned data

        Returns
        -------
        dict
            Verse data with book, chapter, verse fields
        """
        data = {
            "book": cleaned_data["book"],
            "chapter": cleaned_data["chapter"],
        }
        if cleaned_data.get("verse"):
            data["verse"] = cleaned_data["verse"]

        # Could add testament detection, book index, etc.
        return data

    def get_enrichment_type(self):
        """Return enrichment type."""
        return "verse"


class IDEnrichmentForm(BaseTagEnrichmentForm):
    """
    Form for enriching tags with external authority IDs.

    Supports various ID systems like:
    - GND (Gemeinsame Normdatei) for persons, places, organizations
    - GeoNames for geographic locations
    - VIAF for persons
    - Wikidata for any entity
    """

    id_type = forms.ChoiceField(
        label="ID Type",
        choices=[
            ("gnd", "GND (Gemeinsame Normdatei)"),
            ("geonames", "GeoNames"),
            ("viaf", "VIAF"),
            ("wikidata", "Wikidata"),
            ("other", "Other"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="The authority control system or database",
    )

    id_value = forms.CharField(
        label="ID Value",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g., 118540238, 2950159"}
        ),
        help_text="The identifier in the selected system",
    )

    resource_url = forms.URLField(
        label="Resource URL",
        required=False,
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "https://..."}
        ),
        help_text="Direct link to the authority record (optional)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Try to extract ID from variation if it looks like one
        self._populate_from_variation()

    def propose_normalization(self, variation, project):
        """
        Generate normalized label for the entity.

        Parameters
        ----------
        variation : str
            The tag variation text
        project : Project
            Project context

        Returns
        -------
        str
            Proposed normalized name
        """
        # Clean up the variation for use as normalized value
        return variation.strip()

    def _populate_from_variation(self):
        """Try to detect ID type and value from the variation text."""
        variation = self.tag.variation.lower()

        # Check for GND patterns
        if "gnd" in variation or "d-nb.info" in variation:
            self.fields["id_type"].initial = "gnd"
            # Try to extract GND number
            gnd_match = re.search(r"(\d{8,10})", variation)
            if gnd_match:
                self.fields["id_value"].initial = gnd_match.group(1)

        # Check for GeoNames patterns
        elif "geonames" in variation:
            self.fields["id_type"].initial = "geonames"
            geonames_match = re.search(r"(\d{6,8})", variation)
            if geonames_match:
                self.fields["id_value"].initial = geonames_match.group(1)

        # Check for VIAF patterns
        elif "viaf" in variation:
            self.fields["id_type"].initial = "viaf"
            viaf_match = re.search(r"(\d{8,})", variation)
            if viaf_match:
                self.fields["id_value"].initial = viaf_match.group(1)

        # Check for Wikidata patterns
        elif "wikidata" in variation or "Q" in variation:
            self.fields["id_type"].initial = "wikidata"
            wd_match = re.search(r"Q(\d+)", variation, re.IGNORECASE)
            if wd_match:
                self.fields["id_value"].initial = f"Q{wd_match.group(1)}"

    def build_enrichment_data(self, cleaned_data):
        """
        Build structured ID data.

        Parameters
        ----------
        cleaned_data : dict
            Form cleaned data

        Returns
        -------
        dict
            ID data with type, value, and optional URL
        """
        data = {
            "id_type": cleaned_data["id_type"],
            "id_value": cleaned_data["id_value"],
        }

        if cleaned_data.get("resource_url"):
            data["resource_url"] = cleaned_data["resource_url"]

        # Generate standard URL if not provided
        if not data.get("resource_url"):
            data["resource_url"] = self._generate_standard_url(
                cleaned_data["id_type"], cleaned_data["id_value"]
            )

        return data

    def _generate_standard_url(self, id_type, id_value):
        """
        Generate standard URL for common ID systems.

        Parameters
        ----------
        id_type : str
            The ID system type
        id_value : str
            The ID value

        Returns
        -------
        str
            Standard URL for the resource
        """
        url_templates = {
            "gnd": "https://d-nb.info/gnd/{id}",
            "geonames": "https://www.geonames.org/{id}/",
            "viaf": "https://viaf.org/viaf/{id}/",
            "wikidata": "https://www.wikidata.org/wiki/{id}",
        }

        template = url_templates.get(id_type)
        if template:
            return template.format(id=id_value)
        return ""

    def get_enrichment_type(self):
        """Return enrichment type."""
        return "authority_id"


def get_enrichment_form_class(enrichment_type):
    """
    Factory to get form class for enrichment type.

    Parameters
    ----------
    enrichment_type : str
        Type of enrichment (e.g., 'date', 'verse')

    Returns
    -------
    class
        Form class for the enrichment type
    """
    form_map = {
        "date": DateEnrichmentForm,
        "verse": BibleVerseEnrichmentForm,
        "authority_id": IDEnrichmentForm,
    }
    return form_map.get(enrichment_type, BaseTagEnrichmentForm)
