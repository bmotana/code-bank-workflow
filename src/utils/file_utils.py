"""Utility functions for file operations."""

import logging
from pathlib import Path
from typing import Any, Dict, Union

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ConfigurationError(Exception):
    """Exception raised for errors in configuration file operations."""

    pass


def read_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read and parse a YAML configuration file.

    Args:
        file_path (str | Path): Path to the YAML file.

    Returns:
        Dict[str, Any]: Parsed YAML data.

    Raises:
        ConfigurationError: If there are issues reading or parsing the file.
    """
    try:
        with open(file_path) as file:
            return yaml.safe_load(file)
    except (FileNotFoundError, yaml.YAMLError) as error:
        logging.error(f"Configuration error with {file_path}: {error}")
        raise ConfigurationError(f"Failed to load configuration: "
                                 f"{error}") from error
