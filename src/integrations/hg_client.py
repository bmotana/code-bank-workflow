"""
Client for interacting with Hugging Face Inference API.

This module provides a client for making requests,
to Hugging Face's Inference API,allowing users,
to leverage various language models for text generation and code analysis.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from dotenv import load_dotenv

import requests


from src.utils.file_utils import read_yaml

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Define path to default configuration
BASE_CONFIG_PATH = Path(__file__).parents[2] / "config" / "default_config.yaml"


class HuggingFaceError(Exception):
    """Custom exception for Hugging Face API related errors."""

    pass


class HgClient:
    """
    Client for Hugging Face's Inference API for language models.

    This client handles authentication, configuration,
    and API requests to Hugging Face's hosted models,
    providing a simple interface for text generation
    and code analysis tasks.
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        model_name: Optional[str] = None,
        config_path: Optional[Union[Path, str]] = None
    ) -> None:
        """
        Initialize the Hugging Face client.

        Args:
            api_token: Your Hugging Face API token.
                        If None, reads from HF_API_TOKEN
                       environment variable.
            model_name: The specific model to use (e.g.,
                        "Qwen/Qwen2.5-72B-Instruct").
                        If None,
                         uses the default model from configuration.
            config_path: Path to the configuration file.
                        If None, uses the default path.

        Raises:
            ValueError: If no API token is provided or
                        found in environment variables.
            HuggingFaceError: If the configuration is invalid
                        or missing required fields.
        """
        # Get API token from parameters or environment
        if api_token is None:
            api_token = os.environ.get("HF_API_TOKEN")

        if not api_token:
            logger.error("No Hugging Face API token provided")
            raise ValueError(
                "Hugging Face API token is required. Provide it directly or "
                "set the HF_API_TOKEN environment variable."
            )

        # Load and validate configuration
        self.config = self._load_config(config_path)

        # Initialize client attributes
        self.base_url = self.config["huggingface"]["base_url"]
        self.api_token = api_token
        self.model_name = model_name or self.config["huggingface"]["default_model"]  # noqa: E501
        self.api_url = f"{self.base_url}{self.model_name}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

        logger.info(f"HgClient initialized for model: {self.model_name}")

    @staticmethod
    def _load_config(
        config_path: Optional[Union[Path, str]] = None
    ) -> Dict[str, Any]:
        """
        Load and validate configuration from file.

        Args:
            config_path: Path to configuration file.
                        If None, uses the default path.

        Returns:
            Validated configuration dictionary.

        Raises:
            HuggingFaceError: If configuration is invalid or cannot be loaded.
        """
        if config_path is None:
            config_path = BASE_CONFIG_PATH

        try:
            config = read_yaml(config_path)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise HuggingFaceError(f"Failed to load configuration: {e}")

        # Validate required configuration fields
        hg_config = config.get("huggingface", {})
        if not hg_config:
            logger.error("Missing 'huggingface' section in configuration")
            raise HuggingFaceError("Missing 'huggingface'"
                                   " section in configuration")

        if not hg_config.get("base_url"):
            logger.error("Missing required 'base_url' in configuration")
            raise HuggingFaceError("Missing required "
                                   "'base_url' in configuration")

        # Validate other recommended fields
        required_fields = ["models", "default_model", "base_url"]
        for field in required_fields:
            if field not in hg_config:
                logger.warning(f"Missing recommended field"
                               f" '{field}' in configuration")

        return config

    def query(self,
              prompt: str,
              **kwargs: Any) -> Dict[str, Any]:  # noqa: ANN401
        """
        Request completion from Hugging Face model via Inference API.

        Args:
            prompt: The input text/prompt to send to the model.
            **kwargs: Additional parameters to pass in the payload to the API
                     (e.g., parameters={"max_new_tokens": 250}).

        Returns:
            The JSON response from the API containing the model's output
            or an error message if the request failed.
        """
        if not prompt:
            logger.warning("Empty prompt provided to query method")
            return {"error": "Prompt cannot be empty."}

        # Prepare request payload
        payload = {"inputs": prompt}
        if kwargs:
            payload.update(kwargs)

        logger.debug(f"Sending request to"
                     f" {self.api_url} with payload: {payload}")
        response = None
        try:
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60  # Add timeout to prevent hanging requests
            )

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            # Handle specific HTTP errors
            error_message = f"HTTP Error: {http_err}"
            try:
                # Try to get more specific error details from the response body
                error_details = response.json()
                error_message += f" - Details: {error_details}"
            except requests.exceptions.JSONDecodeError:
                # Show raw text if not JSON
                error_message += f" - Response Body: {response.text}"

            logger.error(error_message)
            return {
                "error": error_message,
                "status_code": response.status_code
            }

        except requests.exceptions.RequestException as req_err:
            # Handle other request errors (network issues, DNS errors, etc.)
            logger.error(f"Request Exception: {req_err}")
            return {"error": f"Request Exception: {req_err}"}

        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error during API request: {e}")
            return {"error": f"An unexpected error occurred: {e}"}

    def explain_code(self, code: str) -> str:
        """
        Explain the provided code using the Hugging Face model.

        Analyzes code to identify common pitfalls, edge cases, and provide
        a comprehensive explanation.

        Args:
            code: The source code to analyze.

        Returns:
            A detailed explanation of the code.

        Raises:
            ValueError: If the code is empty.
            HuggingFaceError: If there's an error communicating with the API.
        """
        if not code or not code.strip():
            logger.error("Empty code provided to explain_code")
            raise ValueError("Code cannot be empty")

        logger.info("Generating code explanation")

        prompt = f"""
        Analyze the following code:
        What are the common pitfalls?
        What is the bigger picture?
        What are the edge cases for the following code?
        ```
        {code}
        ```
        """

        try:
            response = self.query(prompt)

            if isinstance(response, dict) and "error" in response:
                logger.error(f"API error during code explanation:"
                             f" {response['error']}")
                raise HuggingFaceError(f"Failed to explain code:"
                                       f" {response['error']}")

            # Extract the generated text from the response
            if isinstance(response, list) and response and "generated_text" in response[0]:  # noqa: E501
                return response[0]["generated_text"]
            else:
                logger.error(f"Unexpected response format: {response}")
                raise HuggingFaceError("Unexpected response format from API")

        except Exception as e:
            logger.error(f"Failed to explain code: {str(e)}")
            raise


def main() -> None:
    """
    Run a simple demonstration of the Hugging Face client.

    This function initializes a client with a specified model and
    demonstrates the code explanation functionality.
    """
    try:
        # Choose a model to use
        # model = "Qwen/Qwen2.5-72B-Instruct"
        model = "mistralai/Mistral-7B-Instruct-v0.1"

        # Initialize the client
        llama = HgClient(model_name=model)

        # Sample code to explain
        code = """
        def add(a, b):
            return a + b
        """

        # Get and print the explanation
        explanation = llama.explain_code(code)
        print(explanation)

    except Exception as e:
        print(f"Error in demonstration: {e}")

