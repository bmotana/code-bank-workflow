import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

# Assuming your client is in src/client/hg_client.py
from src.integrations.hg_client import (BASE_CONFIG_PATH,
                                        HgClient,
                                        HuggingFaceError)

import yaml  # Using pyyaml for creating test config data easily

# Assuming read_yaml is in src/utils/file_utils.py
# If read_yaml is simple, you might mock it directly without importing
# from src.utils.file_utils import read_yaml

# Disable logging clutter during tests
logging.disable(logging.CRITICAL)


# --- Helper function to create dummy config data ---
def create_dummy_config(
        base_url: str = "https://api-inference.huggingface.co/models/",
        default_model: str = "default/model-v1",
        models: str = None
):
    """
    Create a dummy configuration dictionary for testing.

    Args:
        base_url: The base URL for the Hugging Face API
        default_model: The default model name to use
        models: List of available models or None to use defaults

    Returns:
        A dictionary containing the test configuration
    """
    config = {
        "huggingface": {
            "base_url": base_url,
            "default_model": default_model,
            "models": models or ["default/model-v1", "another/model"]
        }
    }
    return config


# --- Test Class ---
class TestHgClient(unittest.TestCase):
    """
    Test suite for the HgClient class.

    Tests initialization, configuration loading, and API interaction
    for the Hugging Face client implementation.
    """

    def setUp(self):
        """Set up for test methods."""
        self.test_token = "dummy_test_token_123"
        self.test_model = "test/model-instruct"
        self.default_config_data = create_dummy_config()
        self.default_base_url = (self.default_config_data["huggingface"]["base_url"])  # noqa: E501
        self.default_model_name = self.default_config_data["huggingface"]["default_model"]  # noqa: E501

        # Create a temporary directory for config files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = Path(self.temp_dir.name)

        # Store original environment variable and clear it for isolation
        self.original_hf_token = os.environ.get("HF_API_TOKEN")
        if "HF_API_TOKEN" in os.environ:
            del os.environ["HF_API_TOKEN"]

    def tearDown(self):
        """Tear down after test methods."""
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        # Restore original environment variable
        if self.original_hf_token is not None:
            os.environ["HF_API_TOKEN"] = self.original_hf_token
        elif "HF_API_TOKEN" in os.environ:
            # Ensure it's removed if it wasn't there originally
            del os.environ["HF_API_TOKEN"]

    # --- Helper to create a temporary config file ---
    def create_temp_config_file(self,
                                config_data: dict,
                                filename: str = "test_config.yaml"):
        """
        Create a temporary configuration file for testing.

        Args:
            config_data: Dictionary containing configuration data
            filename: Name of the temporary file to create

        Returns:
            Path to the created configuration file
        """
        config_path = self.temp_dir_path / filename
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        return config_path

    # --- Initialization Tests ---

    @patch('src.integrations.hg_client.read_yaml')
    def test_init_success_with_token_and_model(self,
                                               mock_read_yaml: MagicMock  # noqa: E501
                                               ) -> None:
        """Test successful initialization with direct token and model."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token,
                          model_name=self.test_model)

        self.assertEqual(client.api_token, self.test_token)
        self.assertEqual(client.model_name, self.test_model)
        self.assertEqual(client.base_url, self.default_base_url)
        self.assertEqual(client.api_url,
                         f"{self.default_base_url}{self.test_model}")
        self.assertEqual(client.headers,
                         {"Authorization": f"Bearer {self.test_token}"})
        mock_read_yaml.assert_called_once_with(BASE_CONFIG_PATH)
        # Default path used

    @patch('src.integrations.hg_client.read_yaml')
    def test_init_success_with_env_var_and_default_model(self,
                                                         mock_read_yaml: MagicMock  # noqa: E501
                                                         ) -> None:
        """Test init using env var token with default model."""
        mock_read_yaml.return_value = self.default_config_data
        os.environ["HF_API_TOKEN"] = self.test_token
        client = HgClient()  # No token or model passed

        self.assertEqual(client.api_token, self.test_token)
        self.assertEqual(client.model_name, self.default_model_name)
        self.assertEqual(client.api_url,
                         f"{self.default_base_url}{self.default_model_name}")
        mock_read_yaml.assert_called_once_with(BASE_CONFIG_PATH)

    @patch('src.integrations.hg_client.read_yaml')
    # Patch where read_yaml is defined/imported
    def test_init_success_with_custom_config_path(self,
                                                  mock_read_yaml: MagicMock
                                                  ) -> None:
        """Test successful initialization with a custom config path."""
        custom_config_data = create_dummy_config(default_model="custom/config-model")  # noqa: E501
        custom_config_path = self.create_temp_config_file(custom_config_data)
        mock_read_yaml.return_value = custom_config_data

        client = HgClient(api_token=self.test_token,
                          config_path=custom_config_path)

        self.assertEqual(client.model_name, "custom/config-model")
        mock_read_yaml.assert_called_once_with(custom_config_path)

    def test_init_fail_no_token(self):
        """Test initialization fails if no token is provided or in env."""
        # Ensure env var is not set
        if "HF_API_TOKEN" in os.environ:
            del os.environ["HF_API_TOKEN"]

        with self.assertRaisesRegex(ValueError,
                                    "Hugging Face API token is required"):
            HgClient()  # No token passed, none in env

    @patch('src.integrations.hg_client.read_yaml')
    def test_init_fail_config_load_error(self,
                                         mock_read_yaml: MagicMock) -> None:
        """Test initialization fails if config loading raises an error."""
        mock_read_yaml.side_effect = FileNotFoundError("Config file not found")
        with self.assertRaisesRegex(HuggingFaceError,
                                    "Failed to load configuration"):
            HgClient(api_token=self.test_token)

    @patch('src.integrations.hg_client.read_yaml')
    def test_init_fail_missing_huggingface_section(self,
                                                   mock_read_yaml: MagicMock
                                                   ) -> None:
        """Test initialization fails if 'huggingface' section is missing."""
        mock_read_yaml.return_value = {"other_section": {}}
        # Missing 'huggingface'
        with self.assertRaisesRegex(HuggingFaceError,
                                    "Missing 'huggingface' section"):
            HgClient(api_token=self.test_token)

    @patch('src.integrations.hg_client.read_yaml')
    def test_init_fail_missing_base_url(self,
                                        mock_read_yaml: MagicMock) -> None:
        """Test initialization fails if 'base_url' is missing."""
        bad_config = {"huggingface": {"default_model": "some/model"}}
        # Missing 'base_url'
        mock_read_yaml.return_value = bad_config
        with self.assertRaisesRegex(HuggingFaceError,
                                    "Missing required 'base_url'"):
            HgClient(api_token=self.test_token)

    # --- _load_config Tests (implicitly tested via __init__,
    # but can add direct tests) ---
    # Note: Testing _load_config directly might require
    # mocking Path or file access differently

    # --- Query Method Tests ---

    @patch('src.integrations.hg_client.requests.post')
    @patch('src.integrations.hg_client.read_yaml')
    def test_query_success(self,
                           mock_read_yaml: MagicMock,
                           mock_post: MagicMock) -> None:
        """Test successful query call."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        # Configure mock response
        mock_response = MagicMock()
        expected_result = [{"generated_text": "This is the model response."}]
        mock_response.json.return_value = expected_result
        mock_response.raise_for_status.return_value = None
        # Simulate success (no exception)
        mock_post.return_value = mock_response

        prompt = "Explain this concept:"
        result = client.query(prompt, parameters={"max_new_tokens": 100})

        self.assertEqual(result, expected_result)
        expected_payload = {"inputs": prompt,
                            "parameters": {"max_new_tokens": 100}}
        mock_post.assert_called_once_with(
            client.api_url,
            headers=client.headers,
            json=expected_payload,
            timeout=60
        )
        mock_response.raise_for_status.assert_called_once()

    @patch('src.integrations.hg_client.read_yaml')
    def test_query_empty_prompt(self, mock_read_yaml: MagicMock) -> None:
        """Test query with an empty prompt returns an error."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)
        result = client.query("")
        self.assertEqual(result, {"error": "Prompt cannot be empty."})

    @patch('src.integrations.hg_client.requests.post')
    @patch('src.integrations.hg_client.read_yaml')
    def test_query_http_error_with_json(self,
                                        mock_read_yaml: MagicMock,
                                        mock_post: MagicMock) -> None:
        """Test query handling HTTPError with JSON body."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        mock_response = MagicMock()
        error_details = {"error": "Model is overloaded", "code": 503}
        mock_response.json.return_value = error_details
        mock_response.status_code = 503
        http_error = requests.exceptions.HTTPError("503 Server Error",
                                                   response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        # Raise error when called
        mock_post.return_value = mock_response

        result = client.query("A valid prompt")

        self.assertIn("error", result)
        self.assertIn("HTTP Error: 503 Server Error", result["error"])
        self.assertIn(str(error_details), result["error"])
        # Check details are included
        self.assertEqual(result.get("status_code"), 503)
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
        # Ensure it was checked

    @patch('src.integrations.hg_client.requests.post')
    @patch('src.integrations.hg_client.read_yaml')
    def test_query_http_error_non_json(self,
                                       mock_read_yaml: MagicMock,
                                       mock_post: MagicMock) -> None:
        """Test query handling HTTPError with non-JSON body."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        mock_response = MagicMock()
        mock_response.text = "Gateway Timeout"
        # Make json() raise an error to simulate non-json response
        mock_response.json.side_effect = (requests.exceptions.
                                          JSONDecodeError("msg",
                                                          "doc", 0))
        mock_response.status_code = 504
        http_error = requests.exceptions.HTTPError("504 Gateway Timeout",
                                                   response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        result = client.query("Another prompt")

        self.assertIn("error", result)
        self.assertIn("HTTP Error: 504 Gateway Timeout", result["error"])
        self.assertIn(f"Response Body: {mock_response.text}",
                      result["error"])  # Check raw text
        self.assertEqual(result.get("status_code"), 504)
        mock_post.assert_called_once()

    @patch('src.integrations.hg_client.requests.post')
    @patch('src.integrations.hg_client.read_yaml')
    def test_query_request_exception(self,
                                     mock_read_yaml: MagicMock,
                                     mock_post: MagicMock) -> None:
        """Test query handling RequestException (e.g., connection error)."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        req_error = requests.exceptions.ConnectionError("Could not connect")
        mock_post.side_effect = req_error  # Raise directly from post

        result = client.query("A prompt")

        self.assertIn("error", result)
        self.assertEqual(result["error"], f"Request Exception: {req_error}")
        mock_post.assert_called_once()

    # --- Explain Code Method Tests ---

    # Use patch.object for mocking methods on an instance we create
    @patch.object(HgClient, 'query')
    @patch('src.integrations.hg_client.read_yaml')
    # Still need to patch read_yaml for init
    def test_explain_code_success(self, mock_read_yaml: MagicMock,
                                  mock_query: MagicMock) -> None:
        """Test successful code explanation."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        code = "def func():\n  pass"
        expected_explanation = "This is the explanation."
        mock_query.return_value = [{"generated_text": expected_explanation}]

        explanation = client.explain_code(code)

        self.assertEqual(explanation, expected_explanation)
        # Check that query was called with the correct prompt structure
        mock_query.assert_called_once()
        call_args, _ = mock_query.call_args
        prompt_arg = call_args[0]
        self.assertIn("Analyze the following code:", prompt_arg)
        self.assertIn("common pitfalls", prompt_arg)
        self.assertIn("bigger picture", prompt_arg)
        self.assertIn("edge cases", prompt_arg)
        self.assertIn(code, prompt_arg)

    @patch('src.integrations.hg_client.read_yaml')
    def test_explain_code_empty_input(self, mock_read_yaml: MagicMock) -> None:
        """Test explain_code raises ValueError for empty code."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        with self.assertRaisesRegex(ValueError, "Code cannot be empty"):
            client.explain_code("")
        with self.assertRaisesRegex(ValueError, "Code cannot be empty"):
            client.explain_code("   \n\t ")  # Whitespace only

    @patch.object(HgClient, 'query')
    @patch('src.integrations.hg_client.read_yaml')
    def test_explain_code_api_error(self,
                                    mock_read_yaml: MagicMock,
                                    mock_query: MagicMock) -> None:
        """Test explain_code raises HuggingFaceError on API error."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        api_error_response = {"error": "Model failed", "status_code": 500}
        mock_query.return_value = api_error_response

        with self.assertRaisesRegex(HuggingFaceError,
                                    "Failed to explain code:.*Model failed"):
            client.explain_code("def test(): pass")
        mock_query.assert_called_once()

    @patch.object(HgClient, 'query')
    @patch('src.integrations.hg_client.read_yaml')
    def test_explain_code_unexpected_format(self,
                                            mock_read_yaml: MagicMock,
                                            mock_query: MagicMock) -> None:
        """Test explain_code raises HuggingFaceError on bad response format."""
        mock_read_yaml.return_value = self.default_config_data
        client = HgClient(api_token=self.test_token)

        # Simulate formats that don't match expected structure
        bad_formats = [
            [],  # Empty list
            [{"wrong_key": "some text"}],
            # List with dict without 'generated_text'
            {"just": "a dict"},  # Not a list
            None  # None response
        ]

        for bad_response in bad_formats:
            mock_query.reset_mock()  # Reset mock for next iteration
            mock_query.return_value = bad_response
            with self.assertRaisesRegex(HuggingFaceError,
                                        "Unexpected response format from API"):
                client.explain_code("def test(): pass")
            mock_query.assert_called_once()


# --- Main execution block ---
if __name__ == '__main__':
    unittest.main()
