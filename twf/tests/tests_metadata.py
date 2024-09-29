from django.test import TestCase

from twf.export_utils import create_data_from_config


class MetadataTransformationTest(TestCase):

    def setUp(self):
        # Example configuration used for transformation
        self.config = {
            "schema": {
                "value": "http://some.url.to/schema.json"
            },
            "project.name.short": {
                "value": "Static title"
            },
            "project.name.long": {
                "value": "Some longer static title"
            },
            "page_number": {
                "value": "p. {page}"
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

        # Example metadata input for the test
        self.metadata = {
            "page": 23,
            "tags1": ["lion", "zebra"],
            "tags2": ["new york", "london"]
        }

        self.expected_output = {
            "schema": "http://some.url.to/schema.json",
            "project": {
                "name": {
                    "short": "Static title",
                    "long": "Some longer static title"
                }
            },
            "page_number": "p. 23",
            "tags": {
                "animals": ["lion", "zebra"],
                "cities": ["new york", "london"]
            }
        }

    def test_transform_metadata_correctly(self):
        """
        Test that metadata is correctly transformed based on the provided configuration.
        """
        # Call the function to transform metadata
        result = create_data_from_config(self.metadata, self.config)

        # Assert the transformed result matches the expected output
        self.assertEqual(result, self.expected_output)

    def test_missing_keys_handled_gracefully(self):
        """
        Test that missing keys in the metadata do not cause errors.
        """
        incomplete_metadata = {
            "page": 23,
            "tags1": ["lion", "zebra"],
            # "tags2" is missing
        }

        # Expected output when tags2 is missing
        expected_output = self.expected_output
        expected_output["tags"]["cities"] = []

        result = create_data_from_config(incomplete_metadata, self.config)

        # Assert that missing keys are handled without errors
        self.assertEqual(result, expected_output)

    def test_empty_metadata(self):
        """
        Test that empty metadata returns an empty or minimally structured result.
        """
        empty_metadata = {}

        # Expected output for empty metadata
        expected_output = self.expected_output
        expected_output["tags"]["animals"] = []
        expected_output["tags"]["cities"] = []
        expected_output["page_number"] = ""

        result = create_data_from_config(empty_metadata, self.config)

        # Assert the transformed result is empty or minimally structured
        self.assertEqual(result, expected_output)
