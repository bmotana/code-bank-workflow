import os
import unittest
from unittest.mock import Mock, patch


from google.api_core.exceptions import GoogleAPIError

from src.integrations.gemini_client import GeminiClient


class TestGeminiClient(unittest.TestCase):
    """Test suite for the GeminiClient class."""

    def setUp(self) -> None:
        """Set up test environment before each test method runs."""
        os.environ["GEMINI_API_KEY"] = "test_api_key"
        self.client = GeminiClient()

    def tearDown(self) -> None:
        """Clean up test environment after each test method runs."""
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

    def test_init_with_explicit_api_key(self) -> None:
        """Test initialization with an explicitly provided API key."""
        client = GeminiClient(api_key="explicit_key")
        self.assertEqual(client.api_key, "explicit_key")
        self.assertEqual(client.model_name, "gemini-2.0-flash")

    def test_init_missing_api_key(self) -> None:
        """Test initialization with missing API key raises ValueError."""
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        with self.assertRaises(ValueError) as context:
            GeminiClient()
        self.assertIn("API key must be provided", str(context.exception))

    @patch('google.genai.Client')
    def test_generate_response_success(self, mock_client: Mock) -> None:
        """Test successful response generation."""
        # Create a new client instance after mocking
        self.client = GeminiClient()

        # Set up the mock response
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_client.return_value.models.generate_content.return_value = mock_response  # noqa: E501

        response = self.client.generate_response("Test input")
        self.assertEqual(response, "Generated response")
        mock_client.return_value.models.generate_content.assert_called_once_with(  # noqa: E501
            model="gemini-2.0-flash",
            contents="Test input"
        )

    def test_generate_response_empty_input(self) -> None:
        """Test that empty input raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.client.generate_response("")
        self.assertIn("Input text cannot be empty", str(context.exception))

        with self.assertRaises(ValueError):
            self.client.generate_response("   ")

    @patch('google.genai.Client')
    def test_generate_response_api_error(self, mock_client: Mock) -> None:
        """Test handling of API errors during response generation."""
        # Instead of importing and creating a ClientError directly,
        # just use a generic exception that your code will catch
        mock_client.return_value.models.generate_content.side_effect = (
            GoogleAPIError("API key not valid. Please pass a valid API key.")
        )

        with self.assertRaises(Exception) as context:
            self.client.generate_response("Test input")
        self.assertIn("API key not valid", str(context.exception))

    def test_explain_code_empty_input(self) -> None:
        """Test that empty code input raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.client.explain_code("")
        self.assertIn("Code cannot be empty", str(context.exception))

        with self.assertRaises(ValueError):
            self.client.explain_code("   ")

    @patch('google.genai.Client')
    def test_explain_code_success(self, mock_client: Mock) -> None:
        """Test successful code explanation generation."""
        # Create a new client instance after mocking
        self.client = GeminiClient()

        mock_response = Mock()
        mock_response.text = "Code explanation"
        mock_client.return_value.models.generate_content.return_value =\
            mock_response

        test_code = "def test(): pass"
        response = self.client.explain_code(test_code)

        self.assertEqual(response, "Code explanation")
        mock_client.return_value.models.generate_content.assert_called_once()
        call_args = (
            mock_client.return_value.models.generate_content.call_args)[1]
        self.assertIn(test_code, call_args["contents"])

    @patch('google.genai.Client')
    def test_explain_code_client_error(self, mock_client: Mock) -> None:
        """Test handling of API errors during code explanation."""
        # Instead of trying to create a ClientError directly,
        # use GoogleAPIError which is already being used in another test
        mock_client.return_value.models.generate_content.side_effect = (
            GoogleAPIError("API key not valid. Please pass a valid API key.")
        )

        with self.assertRaises(Exception) as context:
            self.client.explain_code("def test(): pass")
        self.assertIn("API key not valid", str(context.exception))
