"""
Main window module for Code Bank Workflow application.

This module implements the main application window using tkinter,
serving as the core container for all pages in the application.
It manages page navigation and initialization of different views
including Home, Recall Game, Feynman Technique, and Settings pages.

Classes:
    CodeBankApp: Main application class that inherits from tk.Tk and handles
                 the initialization and navigation between different pages of
                 the application.

Functions:
    main(): Application entry point that initializes and runs the main window.

Usage:
    Run this file directly to start the Code Bank Workflow application:
    $ python main_window.py

Dependencies:
    - tkinter: For GUI implementation
    - logging: For application logging
    - src.gui.home_page: Contains page implementations
"""
import logging
import sys
import tkinter as tk
from tkinter import messagebox  # noqa: F401
from typing import Dict, Type

from src.gui.home_page import (
    FeynmanTechniquePage,
    HomePage,
    RecallGamePage,
    SettingsPage)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("codebank.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class CodeBankApp(tk.Tk):
    """Main application window class for Code Bank Workflow.

    Manages the container frame and navigation between different pages
    including Home, Recall Game, Feynman Technique, and Settings pages.
    Inherits from tk.Tk to provide core window functionality.

    Attributes:
        frames (Dict[str, tk.Frame]): Dictionary mapping names to instances.

    Methods:
        show_frame(page_class): Displays the specified page
        _initialize_pages(container): Sets up all application pages
        _on_closing(): Handles application shutdown procedures
    """

    def __init__(self) -> None:
        """Initialize the main application window.

        Creates the main container frame, configures the window grid,
        and initializes all application pages (Home, Recall Game,
        Feynman Technique, Settings) in a dictionary for easy access
        and navigation.

        Raises:
            tk.TclError: If there's an issue with Tkinter initialization.
            Exception: If there's an unexpected error during initialization.

        Note:
            Sets minimum window size to 800x600 and configures protocol.
        """
        try:
            super().__init__()
            logger.info("Initializing Code Bank Workflow application")

            self.title("Code Bank Workflow")
            # Set minimum window size for better usability
            self.minsize(800, 600)

            # Configure window close event
            self.protocol("WM_DELETE_WINDOW", self._on_closing)

            # Container for all pages
            container = tk.Frame(self)
            container.pack(side="top", fill="both", expand=True)

            # Configure grid weights to ensure proper resizing
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            # Dictionary to hold page references
            self.frames: Dict[str, tk.Frame] = {}

            # Initialize all application pages
            self._initialize_pages(container)
            # Show the home page initially
            self.show_frame(HomePage)
            logger.info("Application initialized successfully")
        except tk.TclError as e:
            logger.critical(f"Failed to initialize Tkinter: {e}")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Unexpected error during initialization: {e}")
            sys.exit(1)

    # noinspection PyTypeChecker
    def _initialize_pages(self, container: tk.Frame) -> None:
        """Initialize and store all application pages in the frames dictionary.

        Creates instances of all page classes and stores them in the frames
        dictionary for later access. Each page is configured to fill the
        entire container using grid layout.

        Args:
            container (tk.Frame): The container frame to hold all pages.

        Raises:
            Exception: If there's an error initializing any page.
        """
        page_classes = (
            HomePage,
            RecallGamePage,
            FeynmanTechniquePage,
            SettingsPage
        )
        for page_class in page_classes:
            try:
                page_name = page_class.__name__
                logger.debug(f"Initializing page: {page_name}")
                frame = page_class(controller=self, parent=container)
                self.frames[page_name] = frame
                # Configure each page to fill the entire container
                frame.grid(row=0, column=0, sticky="nsew")
            except Exception as e:
                logger.error(f"Failed to initialize"
                             f" page {page_class.__name__}: {e}")
                raise

    def show_frame(self, page_class: Type[tk.Frame]) -> None:
        """Bring a specified frame to the front and make it visible.

        This method raises the requested page to the top of the window stack,
        making it visible to the user. If the page has an 'on_show' method,
        it will be called to initialize or refresh the page content.

        Args:
            page_class (Type[tk.Frame]): The class of the page to display.
                                         Should be one of: HomePage,
                                          RecallGamePage,
                                         FeynmanTechniquePage, or SettingsPage.

        Raises:
            KeyError: If the specified page class is not found in dictionary.
            Exception: If there's an error during page  initialization.

        Example:
            self.show_frame(HomePage)  # Navigate to the home page
        """
        try:
            page_name = page_class.__name__
            logger.info(f"Navigating to page: {page_name}")
            if page_name not in self.frames:
                logger.error(f"Page not found: {page_name}")
                raise KeyError(f"Page '{page_name}' not "
                               f"found in application frames")
            frame = self.frames[page_name]
            # Call on_show method if it exists (for page initialization)
            if hasattr(frame, 'on_show') and callable(frame.on_show):
                frame.on_show()
            # Bring the frame to the front
            frame.tkraise()
        except Exception as e:
            logger.error(f"Error showing frame {page_class.__name__}: {e}")
            # Display error message to user
            tk.messagebox.showerror(
                "Navigation Error",
                f"Unable to navigate to the requested page: {str(e)}"
            )

    def _on_closing(self) -> None:
        """Handle application closing event.

        Performs cleanup tasks and closes the application properly.
        This method is called when the user attempts to close the application
        window, ensuring resources are released and any unsaved data is handled
        appropriately before terminating.
        """
        logger.info("Application closing")
        try:
            # Perform any cleanup needed before closing
            # For example, save application state or confirm exit
            self.destroy()
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
            self.destroy()


def main() -> None:
    """Application entry point.

    Creates and runs the main application window. This function initializes
    the CodeBankApp instance and starts the Tkinter main event loop, handling
    any critical exceptions that might occur during execution.

    Returns:
        None

    Raises:
        SystemExit: If a critical error occurs during application execution.

    Example:
        if __name__ == "__main__":
            main()
    """
    try:
        logger.info("Starting Code Bank Workflow application")
        app = CodeBankApp()
        app.mainloop()
        logger.info("Application closed normally")
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}")
        sys.exit(1)


# Run the Application
if __name__ == "__main__":
    main()
