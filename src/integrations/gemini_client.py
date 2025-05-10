"""
Module for interacting with Google's Gemini AI API.

This module provides a client for the Google Gemini AI service, allowing
applications to generate AI responses and analyze code.
It handles authentication,
request formatting, and response parsing.
"""
import logging
import os
from typing import Optional

from dotenv import load_dotenv

from google import genai
from google.api_core.exceptions import GoogleAPIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class GeminiClient:
    """
    Client for interacting with Google's Gemini AI models.

    This class provides methods to generate AI responses and analyze code
    using Google's Gemini models. It handles authentication and request
    formatting.

    Attributes:
        model_name (str): The Gemini model to use for requests
        api_key (str): API key for authentication with Gemini API
        client: The underlying Google Generative AI client
    """

    def __init__(self, api_key: Optional[str] = None,
                 model_name: str = "gemini-2.0-flash") -> None:
        """
        Initialize the Gemini client with credentials and configuration.

        Args:
            api_key: API key for Gemini. If None, will attempt to load from
                    GEMINI_API_KEY environment variable.
            model_name: Name of the Gemini model to use.

        Raises:
            ValueError: If API key is not provided and
                        not found in environment.
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            logger.error("Missing API key for Gemini")
            raise ValueError(
                "API key must be provided or "
                "set as GEMINI_API_KEY environment variable"
            )

        logger.info(f"Initializing Gemini client with model: {model_name}")
        self.client = genai.Client(api_key=self.api_key)

    def generate_response(self, input_text: str) -> str:
        """
        Generate a response from Gemini based on the provided input text.

        Args:
            input_text: The prompt text to send to Gemini.

        Returns:
            The text response from Gemini.

        Raises:
            GoogleAPIError: If there's an error communicating with
                            the Gemini API.
            ValueError: If the input text is empty or invalid.
        """
        if not input_text or not input_text.strip():
            logger.error("Empty input text provided to generate_response")
            raise ValueError("Input text cannot be empty")

        try:
            logger.debug(f"Sending request to Gemini model: {self.model_name}")
            response = self.client.models.generate_content(
                model=self.model_name, contents=input_text
            )
            return response.text
        except GoogleAPIError as e:
            logger.error(f"Error generating response from Gemini: {str(e)}")
            raise

    def explain_code(self, code: str) -> str:
        """
        Analyze code and provide explanation of pitfalls and edge cases.

        This method sends the provided code to Gemini with a prompt asking
        for analysis of potential issues, edge cases, and overall explanation.

        Args:
            code: The source code to analyze.

        Returns:
            A detailed explanation of the code, including potential issues.

        Raises:
            ValueError: If the code is empty.
            GoogleAPIError: If there's an error communicating with
                            the Gemini API.
        """
        if not code or not code.strip():
            logger.error("Empty code provided to explain_code")
            raise ValueError("Code cannot be empty")

        logger.info("Generating code explanation")
        prompt = f"""
        Analyze the following code:
        \n
        Identify common pitfalls, edge cases, and
        provide a comprehensive explanation.
        Include:
        1. Overall purpose and functionality
        2. Potential bugs or issues
        3. Edge cases that might not be handled
        4. Performance considerations
        5. Best practices that could be applied
        \n
        Code:
        ```
        {code}
        ```
        """

        try:
            explanation = self.generate_response(prompt)
            return explanation
        except Exception as e:
            logger.error(f"Failed to explain code: {str(e)}")
            raise
