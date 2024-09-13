from django.test import TestCase

from twf.models import Document, Page, User, Project
from twf.views.export.export_utils import create_data_from_config, create_page_data, create_data


class MetadataTransformationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com'
        )
        self.userprofile = self.user.profile

        self.project = Project(
            title="Test Project",
            collection_id="test_collection",
            description="A test project",
            owner=self.userprofile
        )
        self.project.save(current_user=self.user)

        # Create a sample document
        self.document = Document(
            project=self.project,
            document_id="test_document",
            title="Sample Document",
            metadata={"author": "John Doe", "date": "2024-01-01"}
        )
        self.document.save(current_user=self.user)

        # Create 3 pages associated with the document
        self.page1 = Page(
            document=self.document,
            tk_page_number=1,
            metadata={"tags1": ["lion", "tiger"], "tags2": ["paris", "london"]},
            parsed_data={"text": "Page 1 content"}
        )
        self.page1.save(current_user=self.user)

        self.page2 = Page(
            document=self.document,
            tk_page_number=2,
            metadata={"tags1": ["elephant"], "tags2": ["berlin"]},
            parsed_data={"text": "Page 2 content"}
        )
        self.page2.save(current_user=self.user)

        self.page3 = Page(
            document=self.document,
            tk_page_number=3,
            metadata={"tags1": ["cat"], "tags2": ["new york"]},
            parsed_data={"text": "Page 3 content"}
        )
        self.page3.save(current_user=self.user)

        # Example configuration used for transformation
        self.project.document_export_configuration = {
            "schema": {
                "value": "http://some.url.to/schema.json"
            },
            "transkribus_url": {
                "value": "{__get_transkribus_url__}"
            },
            "project.name.short": {
                "value": "Static title"
            },
            "project.name.long": {
                "value": "Some longer static title"
            },
        }

        self.project.page_export_configuration = {
            "page_number": {
                "value": "p. {__tk_page_number__}"
            },
            "tags.animals": {
                "value": "{tags1}",
                "empty_value": []
            },
            "tags.cities": {
                "value": "{tags2}",
                "empty_value": []
            }
        }
        self.project.save(current_user=self.user)

    def test_metadata_transformation(self):
        print(create_data(self.project))
        print(create_data(self.document))
        print(create_data(self.page1))

