"""Manage code snippets via the Notion API."""

from typing import Any, Dict

import requests


class SnippetManager:
    """Create, read, update, and delete snippets in a Notion database."""

    def __init__(self, notion_api_key: str, database_id: str) -> None:
        """Initialize the manager with Notion credentials."""
        self.notion_api_key = notion_api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def create_snippet(
        self,
        title: str,
        code: str,
        status: str = "Not Started",
    ) -> Dict[str, Any]:
        """Create a new snippet page in Notion."""
        url = "https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": title}}],
                },
                "Status": {
                    "select": {"name": status},
                },
            },
            "children": [
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "text": [{"type": "text", "text": {"content": code}}],
                        "language": "python",
                    },
                },
            ],
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def retrieve_snippets(self) -> Dict[str, Any]:
        """Query all snippets from the configured database."""
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        response = requests.post(url, headers=self.headers)
        return response.json()

    def update_snippet_status(self, page_id: str, new_status: str) -> Dict[str, Any]:
        """Update the status property of a snippet page."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {
            "properties": {
                "Status": {
                    "select": {"name": new_status},
                },
            },
        }
        response = requests.patch(url, headers=self.headers, json=data)
        return response.json()

    def delete_snippet(self, page_id: str) -> int:
        """Delete a snippet block and return the HTTP status code."""
        url = f"https://api.notion.com/v1/blocks/{page_id}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code
