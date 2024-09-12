from django.test import TestCase

from twf.views.export.export_utils import transform_page_metadata


class MetadataTransformationTest(TestCase):

    def setUp(self):
        # Example configuration used for transformation
        self.config = {
            "pages": {
                "page_number": {
                    "value": "p. {page}"
                },
                "tags.animals": {
                    "value": "tags1"
                },
                "tags.cities": {
                    "value": "tags2"
                }
            }
        }

        # Example metadata input for the test
        self.page_metadata = {
            "page": 23,
            "tags1": ["lion", "zebra"],
            "tags2": ["new york", "london"]
        }

    def test_transform_metadata_correctly(self):
        """
        Test that metadata is correctly transformed based on the provided configuration.
        """
        expected_output = {
            "page_number": "p. 23",
            "tags": {
                "animals": ["lion", "zebra"],
                "cities": ["new york", "london"]
            }
        }

        # Call the function to transform metadata
        result = transform_page_metadata(self.page_metadata, self.config)

        # Assert the transformed result matches the expected output
        self.assertEqual(result, expected_output)

    def test_missing_keys_handled_gracefully(self):
        """
        Test that missing keys in the metadata do not cause errors.
        """
        incomplete_metadata = {
            "page": 23,
            "tags1": ["lion"]
            # "tags2" is missing
        }

        # Expected output when tags2 is missing
        expected_output = {
            "page_number": "p. 23",
            "tags": {
                "animals": ["lion"],
                "cities": []  # Should handle missing tags2 gracefully
            }
        }

        result = transform_page_metadata(incomplete_metadata, self.config)

        # Assert that missing keys are handled without errors
        self.assertEqual(result, expected_output)

    def test_empty_metadata(self):
        """
        Test that empty metadata returns an empty or minimally structured result.
        """
        empty_metadata = {}

        # Expected output for empty metadata
        expected_output = {
            "page_number": "p. ",
            "tags": {
                "animals": [],
                "cities": []
            }
        }

        result = transform_page_metadata(empty_metadata, self.config)

        # Assert the transformed result is empty or minimally structured
        self.assertEqual(result, expected_output)
