"""
Notion API Client.

This module provides a NotionClient class for interacting with the Notion API.
It handles database operations and code snippet extraction with
improved error handling and type safety.

Features:
- Load and query Notion databases
- Retrieve and parse Notion pages
- Extract structured code snippets from Notion content
- Comprehensive error handling and logging
- Type-safe operations with TypedDict support
"""
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Tuple, TypedDict, Union
)

from dotenv import load_dotenv

import requests

from src.utils.file_utils import read_yaml

load_dotenv()

DEFAULT_CACHE_SIZE = 32
BASE_CONFIG_PATH = Path(__file__).parents[2] / "config" / "default_config.yaml"

DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format=DEFAULT_LOG_FORMAT
)


class NotionConfig(TypedDict):
    """Type-safe configuration structure."""

    base_url: str
    headers: Dict[str, str]
    database_ids: Dict[str, str]
    notion: Dict[str, Dict[str, str]]


class RequestKwargs(TypedDict, total=False):
    """Type-safe request kwargs."""

    json: Dict[str, Any]
    params: Dict[str, str]
    timeout: int
    # add other expected kwargs


class NotionError(Exception):
    """Custom exception for Notion-related errors."""

    pass


@dataclass(frozen=True)
class CodebankEntry:
    """Structured representation of a code snippet.

    Attributes:
        title: Description of the code snippet
        display_code: Formatted code string with newlines
        exercise_code: Tuple of individual code lines
        status: Current status of the snippet (e.g., "Active", "Archived")
    """

    title: str
    display_code: str
    exercise_code: Tuple[str, ...]
    status: str


@dataclass
class DatabaseItem:
    """Structured representation of a database item from Notion.

    Attributes:
        description: The title/description of the database item
        id: Unique identifier for the item in Notion
        status: Current status of the item (e.g., "Active", "Archived")
    """

    description: str
    id: str
    status: str


class NotionClient:
    """Client for interacting with the Notion API."""

    def __init__(
            self,
            notion_api_key: str,
            database_id: str,
            config_path: Optional[Union[Path, str]] = None
    ) -> None:
        """
        Initialize the NotionClient.

        Args:
            notion_api_key(str): Notion API key for authentication.
            database_id(str): Target database identifier.
            config_path(Optional[Path | str]): Optional path
            to configuration file.

        Raises:
            NotionError: If configuration cannot be loaded or is invalid.
        """
        if not notion_api_key or not database_id:
            raise NotionError("API key and database ID are required")

        self.config = self._load_config(config_path)
        self.notion_api_key = notion_api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            **self.config.get("notion", {}).get("headers", {})
        }
        self.base_url = self.config["notion"]["base_url"]
        self.database_url = f"{self.base_url}/databases/{database_id}/query"

    @staticmethod
    @lru_cache(maxsize=DEFAULT_CACHE_SIZE)
    def _load_config(
            config_path: Optional[Union[Path, str]] = None
    ) -> Dict[str, Any]:
        """
        Load and validate configuration from file.

        Args:
            config_path (Optional[Union[Path, str]]): Path to
            configuration file.

        Returns:
            Dict[str, Any]: Validated configuration dictionary.

        Raises:
            NotionError: If configuration is invalid or cannot be loaded.
        """
        if config_path is None:
            config_path = BASE_CONFIG_PATH

        config = read_yaml(config_path)

        # Validate required configuration fields
        notion_config = config.get("notion", {})
        if not notion_config.get("base_url"):
            raise NotionError("Missing required 'base_url' in configuration")

        # Validate other required fields
        required_fields = ["headers", "codebank_url"]
        for field in required_fields:
            if field not in notion_config:
                logging.warning(
                    f"Missing recommended field '{field}' in configuration")

        return config

    def _make_request(
            self,
            method: str,
            url: str,
            **kwargs: RequestKwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Notion API with error handling.

        Args:
            method(str): HTTP method to use.
            url(str): Target URL.
            **kwargs (Any): Additional request parameters.

        Returns:
            Dict[str, Any]:JSON response from the API.

        Raises:
            NotionError: If the request fails or returns an error.
        """
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            logging.error(f"API request failed: {error}")
            raise NotionError(f"API request failed: {error}") from error

    def load_database(self) -> Dict[str, Any]:
        """
        Fetch data from the configured Notion database.

        Returns:
            Dict[str, Any]:JSON response containing database entries.

        Raises:
            NotionError: If the database cannot be loaded.

        Reference: scratches/notion/for_rewarding/scratch.py

        """
        # TODO: Implement pagination to get all results
        logging.info(f"Loading database: {self.database_id}")
        return self._make_request("POST", self.database_url)

    @staticmethod
    def extract_database_items(data: Dict[str, Any]) -> List[DatabaseItem]:
        """
        Extract database items with improved type safety.

        Args:
            data(Dict[str, Any]): JSON response from Notion API.

        Returns:
            List[DatabaseItem]:List of DatabaseItem objects.

        Raises:
            NotionError: If data cannot be parsed.
        """
        try:
            results = data.get("results", [])
            return [
                DatabaseItem(
                    description=result["properties"]
                    ["Code Description"]["title"][0]["text"]["content"],
                    id=result["id"],
                    status=result["properties"]["Status"]["status"]["name"],

                )
                for result in results
            ]
        except (KeyError, IndexError, TypeError) as error:
            logging.error(f"Failed to parse database items: {error}")
            raise NotionError("Invalid database response structure") from error

    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """
        Retrieve a Notion page's content.

        Args:
            page_id(str): Target page identifier.

        Returns:
            Dict[str, Any]:Page content as JSON.

        Raises:
            NotionError: If the page cannot be retrieved.
        """
        url = f"{self.base_url}/blocks/{page_id}/children"
        return self._make_request("GET", url)

    @staticmethod
    def extract_code_snippet(page_content: Dict[str, Any]) -> Tuple[str, ...]:
        """
        Extract code snippets from page content.

        Args:
            page_content (Dict[str, Any]): Page content as JSON.

        Returns:
            Tuple[str, ...]:Tuple of code snippet lines.

        Raises:
            NotionError: If code snippet cannot be extracted.
        """
        try:
            results = page_content.get("results", [])
            formatted_code = results[0]["code"]["rich_text"][0]["plain_text"]
            return tuple(formatted_code.split("\n"))
        except (KeyError, IndexError, TypeError) as error:
            logging.error(f"Failed to extract code snippet: {error}")
            raise NotionError("Invalid page content structure") from error


@lru_cache(maxsize=DEFAULT_CACHE_SIZE)
def fetch_code_snippet(snippet_index: int = 0) -> tuple[str, tuple[str, ...]]:
    """
    Retrieve and format a specific code snippet from the Notion database.

    Args:
        snippet_index(int): Index of the desired code snippet (default: 0)

    Returns:
        tuple[str, tuple[str, ...]]:A tuple containing:
            - Formatted code string with newlines
            - Tuple of individual code snippet lines

    Raises:
        NotionError: If there are issues accessing or parsing the snippet
    """
    notion_api_key = os.environ.get("NOTION_API_TOKEN")
    codebank_database_id = os.environ.get("CODEBANK_DATABASE_ID")
    client = NotionClient(notion_api_key, codebank_database_id)
    data = client.load_database()
    pages = client.extract_database_items(data)
    logging.info(f"{len(pages)} Pages Found")
    page_contents = client.get_page_content(pages[snippet_index].id)
    snippet = client.extract_code_snippet(page_contents)
    code_string = "\n".join(snippet)
    return code_string + "\n", snippet


@lru_cache(maxsize=DEFAULT_CACHE_SIZE)
def fetch_all_codebank_entries() -> List[CodebankEntry]:
    """
    Retrieve all code snippets and their metadata from the codebank database.

    Returns:
        List[Dict[str, Union[str, Tuple[str, ...]]]]:
        List of dictionaries containing:
            - title: Description of the code snippet
            - display_code: Formatted code string with newlines
            - exercise_code: Tuple of code lines
            - status: Current status of the snippet

    Raises:
        NotionError: If there are issues accessing or parsing the codebank data
    """
    notion_api_key = os.environ.get("NOTION_API_TOKEN")
    codebank_database_id = os.environ.get("CODEBANK_DATABASE_ID")
    client = NotionClient(notion_api_key, codebank_database_id)
    data = client.load_database()
    pages = client.extract_database_items(data)
    logging.info(f"{len(pages)} Pages Found")
    codebank_entries = []
    for page in pages:
        page_content = client.get_page_content(page.id)
        code_snippet = client.extract_code_snippet(page_content)
        codebank_entries.append(CodebankEntry(
            title=page.description,
            display_code="\n".join(code_snippet),
            exercise_code=code_snippet,
            status=page.status
        ))
    return codebank_entries
