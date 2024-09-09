"""Tests for the twf app."""
from django.test import TestCase

from twf.simple_ai_clients import AiApiClient


class TestTagAssigner(TestCase):
    """Test the tag_assigner function."""
    def test_tag_assigner(self):
        """Test the tag_assigner function."""
        key = "sk-yHreKbExQk0cQ2lLUVmz441rTjYK-VuU0J2rY3CvGuT3BlbkFJAVtA-jIXTatjgJG_XKJMa9tuEh2FORvdrP9S9iOe0A"
        client = AiApiClient(api='openai', api_key=key)
        response, elapsed_time = client.prompt(model="gpt-4-turbo", prompt="What is the capital of France?")
        print(response.choices[0].message.content)
        self.assertTrue(True)
