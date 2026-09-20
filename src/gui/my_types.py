"""Shared GUI typing protocols."""

from typing import Protocol


class CodeBankApp(Protocol):
    """Protocol for the main application controller."""

    def __init__(self) -> None:
        """Initialize protocol attributes."""
        self.frames = None

    def show_frame(self, frame_class: type) -> None:
        """Navigate to the given frame class."""
        pass
