"""Code Bank Application Home Page Module.

This module contains the main UI components for the Code Bank application including: # noqa: E501
- Home page navigation
- Code recall game functionality
- Feynman technique interface
- Application settings

Classes:
    HomePage: Main navigation hub
    RecallGamePage: Code memorization game interface
    FeynmanTechniquePage: Learning technique interface
    SettingsPage: Application configuration interface
"""
import logging
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import List, Optional, Union

from pygments.lexers import get_all_lexers

from src.gui.my_types import CodeBankApp
from src.integrations.gemini_client import GeminiClient
from src.integrations.notion_client \
    import CodebankEntry, fetch_all_codebank_entries, fetch_code_snippet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='codebank.log'
)
logger = logging.getLogger(__name__)


class CodeLoopFrame(tk.Frame):
    """
    Frame widget for displaying and managing code snippets.

    Inherits from tkinter.Frame and provides functionality to:
    - Display code snippets with syntax highlighting
    - Show code metadata and status
    - Handle user interactions with code display
    """

    def __init__(self,
                 parent: tk.Frame,
                 code_info: CodebankEntry,
                 controller: CodeBankApp):
        """
        Initialize the code display frame.

        Args:
            parent: Parent tkinter Frame widget
            code_info: Dictionary containing code snippet information
             and metadata
        """
        super().__init__(parent)
        # self.parent = parent
        self.controller = controller
        self.grid_columnconfigure(0, weight=1, uniform='column')
        self.grid_columnconfigure(1, weight=2, uniform='column')
        self.grid_columnconfigure(2, weight=1, uniform='column')

        # Boundary line
        self.section_separator = ttk.Separator(self)
        self.section_separator.grid(row=0,
                                    column=0,
                                    columnspan=3,
                                    sticky='ew',
                                    pady=5)

        # Title section - Column 1
        self.title_frame = tk.Frame(self)
        self.title_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        self.title_label = tk.Label(self.title_frame,
                                    text=code_info.title,
                                    font=('Arial', 12, 'bold'))
        self.title_label.pack(anchor='center', expand=True)

        # Code section - Column 2
        self.code_frame = tk.Frame(self)
        self.code_frame.grid(row=1, column=1, sticky='nsew', padx=5)
        self.code_text = tk.Text(self.code_frame, height=6, wrap='none')
        self.code_text.pack(fill='both', expand=True)
        self.code_text.insert('end', code_info.display_code)

        # Progress and button section - Column 3
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.grid(row=1, column=2, sticky='nsew', padx=5)

        self.progress = ttk.Progressbar(self.bottom_frame)
        self.progress.pack(fill='x', expand=True, padx=(0, 5))
        if code_info.status == 'Not started':
            self.progress['value'] = 0
            self.action_button = ttk.Button(
                self.bottom_frame,
                text="Start",
                command=lambda: self._navigate_with_code_info(
                    RecallGamePage, code_info))
            self.action_button.pack()
        elif code_info.status == 'In progress':
            self.progress['value'] = 50
            self.action_button = ttk.Button(
                self.bottom_frame,
                text="Continue",
                command=lambda: self._navigate_with_code_info(
                    FeynmanTechniquePage, code_info))
            self.action_button.pack()
        else:
            self.progress['value'] = 100
            self.action_button = ttk.Button(self.bottom_frame,
                                            text="done",
                                            state='disabled')
            self.action_button.pack()

    def _navigate_with_code_info(self, class_type: Optional[type],
                                 code_info: CodebankEntry) -> None:
        """
            Navigate to the specified frame and pass code information to it.

        Args:
            class_type: The class of the frame to navigate to
            code_info: The code information to pass to the destination frame
        """
        frame = self.controller.frames[class_type.__name__]
        frame.set_code_info(code_info)
        self.controller.show_frame(class_type)


class HomePage(tk.Frame):
    """Main navigation page providing access to core application features."""

    def __init__(self, parent: Union[tk.Frame, tk.Tk],
                 controller: CodeBankApp):
        """Initialize HomePage with navigation buttons.

        Args:
            parent: Parent tkinter window
            controller: Main application controller

        """
        super().__init__(parent)
        self.controller = controller
        self.codebank_display_data = fetch_all_codebank_entries()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configure and layout UI elements."""
        # Create title label
        self._create_title()
        self._populate_code_frames()
        # Create navigation buttons
        self._create_navigation_buttons()

    def _create_title(self) -> None:
        """Create and position page title."""
        label = tk.Label(self, text="Home Page", font=("Arial", 18))
        label.pack(pady=10, padx=10)

    def _create_navigation_buttons(self) -> None:
        """Create and position navigation buttons."""
        buttons = [
            ("Go to Recall Game", RecallGamePage),
            ("Go to Feynman Technique", FeynmanTechniquePage),
            ("Go to Settings", SettingsPage)
        ]

        for text, page in buttons:
            btn = ttk.Button(
                self,
                text=text,
                command=lambda p=page: self.controller.show_frame(p)
            )
            btn.pack()

    def _populate_code_frames(self) -> List[CodeLoopFrame]:
        """
        Set up and populate the code information GUI elements.

        Creates CodeLoopFrame instances for each code item in the codebank data
        and adds them to the UI.

        Returns:
            List of CodeLoopFrame instances created for displaying
            code information
        """
        frames = []
        for code_item in self.codebank_display_data:
            loop_frame = CodeLoopFrame(self, code_item, self.controller)
            loop_frame.pack(fill='both', expand=True, pady=10)
            frames.append(loop_frame)
        return frames


class RecallGamePage(tk.Frame):
    """
    Interactive game interface for code recall practice.

    This class provides a UI for the recall game
    where users are shown code snippets
    and must recall them from memory after they disappear.
    """

    def __init__(self, parent: Union[tk.Frame, tk.Tk],
                 controller: CodeBankApp) -> None:
        """
        Initialize game interface with code displays and controls.

        Args:
            parent: Parent tkinter window
            controller: Main application controller for navigation
        """
        super().__init__(parent)
        self.controller = controller

        # Game state variables
        self.display_code: str = ""
        self.exercise_code_lines: List[str] = []
        self.current_level: int = 1

        # Set up the UI components
        self._create_ui()

        # Initialize with sample code
        self._initialize_code()
        logger.info("RecallGamePage initialized")

    def set_code_info(self, code_info: CodebankEntry) -> None:
        """
        Set the code information for the game and update the display.

        Args:
            code_info: The code entry containing display code (shown to user)
                      and exercise code (used for practice exercises)

        Updates the sample code and other sample code from the provided
        code info, refreshes the code display, and applies syntax
        highlighting.
        """
        self.display_code, self.exercise_code_lines = (code_info.display_code,
                                                       code_info.exercise_code)
        self.challenge_display.delete("1.0", tk.END)
        self.challenge_display.insert("1.0", self.display_code)
        logger.debug(f"Sample code loaded: {self.display_code[:30]}...")
        self.apply_syntax_highlighting()
        self.update_line_numbers()

    def _create_ui(self) -> None:
        """Create and arrange all UI elements for the game page."""
        # Page title
        self._create_header()

        # Main container frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Language selection area
        self._create_language_selection()

        # Create game button
        self.start_button = ttk.Button(
            self.main_frame,
            text="Start Game",
            command=self.start_game
        )
        self.start_button.pack(pady=(0, 10))

        # Code display areas
        self._create_code_displays()

        # Code input area
        self._create_input_area()

        # Button controls
        self._create_control_buttons()

        # Navigation
        self._create_navigation()
        # we could add a next button that takes

    def _create_header(self) -> None:
        """Create the page header with title."""
        label = tk.Label(self, text="Recall Game", font=("Arial", 18))
        label.pack(pady=10, padx=10)

    def _create_language_selection(self) -> None:
        """Create language selection dropdown and associated UI elements."""
        self.lang_frame = ttk.Frame(self.main_frame)
        self.lang_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(self.lang_frame,
                  text="Language:").pack(side="left", padx=(0, 5))

        try:
            self.languages = sorted([x[0] for x in get_all_lexers()])
        except Exception as e:
            logger.error(f"Error getting lexers: {e}")
            self.languages = ["Python", "JavaScript", "Text"]

        self.selected_language = tk.StringVar(value="Python")
        self.language_dropdown = ttk.Combobox(
            self.lang_frame,
            textvariable=self.selected_language,
            values=self.languages,
            state="readonly"
        )
        self.language_dropdown.pack(side="left")
        self.language_dropdown.bind(
            '<<ComboboxSelected>>',
            lambda x: self.apply_syntax_highlighting()
        )

    def _create_code_displays(self) -> None:
        """Create the code display areas with line numbers."""
        # First code display area (for displaying the challenge)
        self.challenge_frame = ttk.Frame(self.main_frame)
        self.challenge_frame.pack(pady=(0, 10))

        # Line numbers for first display
        self.challenge_line_numbers = tk.Text(
            self.challenge_frame,
            width=4,
            height=10,
            background='lightgray',
            state='disabled',
            font=('Courier New', 12)
        )
        self.challenge_line_numbers.pack(side="left")

        # Main code display
        self.challenge_display = scrolledtext.ScrolledText(
            self.challenge_frame,
            wrap=tk.NONE,
            width=80,
            height=10,
            font=('Courier New', 12)
        )
        self.challenge_display.pack(side="left")

        # Second code display area (for user input)
        self.answer_frame = ttk.Frame(self.main_frame)
        self.answer_frame.pack(pady=(0, 10))

        # Line numbers for second display
        self.answer_line_numbers = tk.Text(
            self.answer_frame,
            width=4,
            height=10,
            background='lightgray',
            state='disabled',
            font=('Courier New', 12)
        )
        self.answer_line_numbers.pack(side="left")

        # User input code display
        self.answer_input = scrolledtext.ScrolledText(
            self.answer_frame,
            wrap=tk.NONE,
            width=80,
            height=10,
            font=('Courier New', 12)
        )
        self.answer_input.pack(side="left")

        # Bind events
        self._bind_events()

    def _bind_events(self) -> None:
        """Set up event bindings for interactive elements."""
        # Bind events for the first code display
        self.challenge_display.bind('<Key>', self.update_line_numbers)
        self.challenge_display.bind('<MouseWheel>', self.update_line_numbers)

        # Bind events for the second code display
        self.answer_input.bind('<Key>', self.update_line_numbers)
        self.answer_input.bind('<MouseWheel>', self.update_line_numbers)
        self.answer_input.bind('<Escape>',
                               lambda e: self._return_to_home_on_escape())

    def _return_to_home_on_escape(self) -> None:
        """Handle the Escape key press to return to the home page."""
        try:
            self.controller.show_frame(HomePage)
        except Exception as e:
            logger.error(f"Error navigating to HomePage: {e}")
            messagebox.showerror("Navigation Error",
                                 "Could not return to the home page.")

    def _create_input_area(self) -> None:
        """Create the input area for adding new code."""
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Add new code")
        self.input_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.code_input = scrolledtext.ScrolledText(
            self.input_frame,
            wrap=tk.NONE,
            width=80,
            height=3,
            font=('Courier New', 12)
        )
        self.code_input.pack(fill="both", expand=True, padx=5, pady=5)

    def _create_control_buttons(self) -> None:
        """Create control buttons for adding and clearing code."""
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill="x", pady=(0, 10))

        self.add_button = ttk.Button(
            self.button_frame,
            text="Add Code",
            command=self.add_code
        )
        self.add_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(
            self.button_frame,
            text="Clear All",
            command=self.clear_code
        )
        self.clear_button.pack(side="left", padx=5)

    def _create_navigation(self) -> None:
        """Create navigation buttons."""
        home_btn = ttk.Button(
            self.main_frame,
            text="Back to Home",
            command=lambda: self._safely_return_to_home()
        )
        home_btn.pack()

    def _safely_return_to_home(self) -> None:
        """Navigate back to the home page safely."""
        try:
            self.controller.show_frame(HomePage)
        except Exception as e:
            logger.error(f"Error navigating to HomePage: {e}")
            messagebox.showerror("Navigation Error",
                                 "Could not return to the home page.")

    def _initialize_code(self) -> None:
        """Initialize code samples and UI state."""
        try:
            # Get sample code for the game

            self.display_code, self.exercise_code_lines = fetch_code_snippet()

            self.challenge_display.insert("1.0", self.display_code)

            # Set initial game state
            self.current_level = 1

            # Apply syntax highlighting and update line numbers
            self.apply_syntax_highlighting()
            self.update_line_numbers()

            logger.debug(f"Sample code loaded: {self.display_code[:30]}...")
        except Exception as e:
            logger.error(f"Error initializing code: {e}")
            messagebox.showerror("Initialization Error",
                                 "Could not load code samples.")

    def apply_syntax_highlighting(self) -> None:
        """Apply syntax highlighting to both code display areas."""
        try:
            # For code display one
            self._prepare_text_widget_for_code(
                self.challenge_display,
                self.selected_language.get()
            )

            # For code display two
            self._prepare_text_widget_for_code(
                self.answer_input,
                self.selected_language.get()
            )
        except Exception as e:
            logger.error(f"Error applying syntax highlighting: {e}")

    @staticmethod
    def _prepare_text_widget_for_code(text_widget: scrolledtext.ScrolledText,
                                      language: str) -> None:
        """
        Apply syntax highlighting to a specific text widget based on language.

        Args:
            text_widget: The text widget to apply highlighting to
            language: The programming language to use for highlighting rules

        Preserves the original text content while applying color and
        style formatting appropriate for the specified programming language.
        """
        code = text_widget.get("1.0", tk.END)

        try:

            # Preserve cursor position while replacing the text
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", code)  # Insert original code

            # Configure text tags for syntax highlighting
            text_widget.tag_configure("code",
                                      foreground="#f8f8f2",
                                      background="#272822")
            text_widget.tag_add("code", "1.0", tk.END)
        except Exception:
            logger.warning(f"Could not find lexer for"
                           f" {language}, using text lexer")

    def update_line_numbers(self, event: Optional[tk.Event] = None) -> None:
        """
        Update line numbers in both code display areas.

        Args:
            event: The triggering event (optional)
        """
        try:
            # Update line numbers for first code area
            self._sync_line_numbers_with_text(self.challenge_line_numbers,
                                              self.challenge_display)

            # Update line numbers for second code area
            self._sync_line_numbers_with_text(self.answer_line_numbers,
                                              self.answer_input)
        except Exception as e:
            logger.error(f"Error updating line numbers: {e}")

    @staticmethod
    def _sync_line_numbers_with_text(
            line_widget: tk.Text,
            text_widget: scrolledtext.ScrolledText) -> None:
        """
        Update line numbers in the line_widget to match content in text_widget.

        Args:
            line_widget: The text widget displaying line numbers
            text_widget: The main text widget containing code content

        Counts the lines in text_widget and updates line_widget with
        corresponding line numbers, ensuring they stay synchronized
        during scrolling and editing.
        """
        # Count lines in the text widget
        text = text_widget.get("1.0", tk.END)
        line_count = len(text.split('\n')) - 1

        # Update the line numbers widget
        line_widget.config(state='normal')
        line_widget.delete("1.0", tk.END)
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        line_widget.insert("1.0", line_numbers_text)
        line_widget.config(state='disabled')

    def add_code(self) -> None:
        """Add new code from the input area to the main code display."""
        try:
            new_code = self.code_input.get("1.0", tk.END).strip()
            if not new_code:
                messagebox.showwarning("Warning", "Enter some code to add!")
                return

            # Add the new code to the display
            current_code = self.challenge_display.get("1.0", tk.END)
            separator = "\n\n" if current_code.strip() else ""
            self.challenge_display.insert(tk.END, separator + new_code)

            # Clear the input area
            self.code_input.delete("1.0", tk.END)

            # Update UI
            self.apply_syntax_highlighting()
            self.update_line_numbers()

            logger.info("New code added to display")
        except Exception as e:
            logger.error(f"Error adding code: {e}")
            messagebox.showerror("Error", f"Could not add code: {e}")

    def clear_code(self) -> None:
        """Clear all code from the main code display after confirmation."""
        try:
            if messagebox.askyesno("Confirm",
                                   "Are you sure you want to clear all code?"):
                self.challenge_display.delete("1.0", tk.END)
                self.update_line_numbers()
                logger.info("All code cleared from display")
        except Exception as e:
            logger.error(f"Error clearing code: {e}")
            messagebox.showerror("Error", f"Could not clear code: {e}")

    def start_game(self) -> None:
        """Start the recall game by showing the first level of code."""
        try:
            self.show_code()
            self.answer_input.bind('<Shift-Return>', self._check_answer)
            logger.info("Game started")
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            messagebox.showerror("Error", "Could not start the game.")

    def show_code(self, level: int = 1) -> None:
        """
        Show code for the current level and then hide it after a delay.

        Args:
            level: The current game level (determines how many lines to show)
        """
        try:
            # Validate level bounds
            if level < 1 or level > len(self.exercise_code_lines):
                logger.warning(f"Invalid level requested: {level}")
                level = min(max(1, level), len(self.exercise_code_lines))

            # Clear both displays
            self.challenge_display.delete("1.0", tk.END)
            self.answer_input.delete("1.0", tk.END)

            # Configure the second display for waiting state
            self._set_answer_input_to_waiting_state()

            # Insert the code for the current level
            code_to_display = "\n".join(self.exercise_code_lines[:level])
            self.challenge_display.insert(tk.END, code_to_display)

            # Schedule UI updates after delay
            self._schedule_code_challenge_transitions()

            logger.info(f"Showing code for level {level}")
        except Exception as e:
            logger.error(f"Error showing code: {e}")
            messagebox.showerror("Game Error",
                                 "Error displaying the code challenge.")

    def _set_answer_input_to_waiting_state(self) -> None:
        """Set second display to waiting state (disabled & red background)."""
        self.answer_input.config(state='disabled')
        self.answer_input.configure(bg='#ff2A00')
        self.answer_input.config(cursor="wait")

    def _schedule_code_challenge_transitions(self,
                                             delay_ms: int = 5000) -> None:
        """
        Schedule UI updates to occur after a specified delay.

        Args:
            delay_ms: The delay in milliseconds before updates occur

        Schedules several actions to occur after the delay:
        - Clears the challenge code from the first display
        - Enables the answer input area for user entry
        - Resets the answer input background color
        - Changes the cursor back to normal
        """
        # Clear the challenge code after delay
        self.challenge_display.after(
            delay_ms,
            lambda index: self.challenge_display.delete(index, tk.END),
            "1.0"
        )

        # Enable the answer input area after delay
        self.answer_input.after(
            delay_ms,
            lambda state: self.answer_input.config(state=state),
            'normal'
        )

        # Reset the answer input background color after delay
        self.answer_input.after(
            delay_ms,
            lambda background: self.answer_input.configure(bg=background),
            'white'
        )

        # Reset the cursor after delay
        self.answer_input.after(
            delay_ms,
            lambda cursor_type: self.answer_input.config(cursor=cursor_type),
            "arrow"

        )

    def _check_answer(self, event: Optional[tk.Event] = None) -> None:
        """
        Check if the user's answer matches the expected code.

        Args:
            event: The triggering event (optional)
        """
        try:
            # Get user's input and expected solution
            user_answer = self.answer_input.get("1.0", tk.END).strip()
            expected_answer = "\n".join(
                self.exercise_code_lines[:self.current_level]
            ).strip()
            logger.debug(f"Expected answer: {expected_answer}")
            logger.debug(f"User answer: {user_answer}")

            # Check if input is empty
            if not user_answer:
                messagebox.showerror("Error",
                                     "Enter your answer before checking.")
                return

            logger.debug(f"Checking answer for level {self.current_level}")

            # Check if the answer is correct
            if self._is_correct_answer(user_answer, expected_answer):
                self._handle_correct_answer()
            else:
                self._handle_incorrect_answer()

        except Exception as e:
            logger.error(f"Error checking answer: {e}")
            messagebox.showerror("Game Error", "Error checking your answer.")

    @staticmethod
    def _is_correct_answer(user_answer: str, expected_answer: str) -> bool:
        """
        Check if the user's answer matches the expected code exactly.

        Args:
            user_answer: The user's input code (after stripping)
            expected_answer: The expected code solution (after stripping)

        Returns:
            True if the answers match exactly (case-sensitive), False otherwise
        """
        return user_answer == expected_answer

    def _handle_correct_answer(self) -> None:
        """Handle the case when the user gives a correct answer."""
        # Check if this was the last level
        if self.current_level >= len(self.exercise_code_lines):
            # TOCHANGE: Make game over move to the next one
            self.game_over()
            logger.info("Game completed successfully")
        else:
            # Move to the next level
            self.current_level += 1
            self.show_code(self.current_level)
            logger.info(f"Level advanced to {self.current_level}")

    def _handle_incorrect_answer(self) -> None:
        """Handle the case when the user gives an incorrect answer."""
        # Reset the current level (don't advance)
        self.show_code(self.current_level)
        self.answer_input.delete("1.0", tk.END)
        logger.info(f"Incorrect answer at level {self.current_level}")

    def game_over(self) -> None:
        """End the game and display the game over state."""
        try:
            # Disable and highlight both display areas
            for display in [self.answer_input, self.challenge_display]:
                display.delete("1.0", tk.END)
                display.config(state='disabled')
                display.configure(bg='#ff2A00')

            # Show game completion message
            messagebox.showinfo(
                "Game Over",
                "Congratulations! You've completed all levels."
            )
            logger.info("Game over")
        except Exception as e:
            logger.error(f"Error in game over: {e}")


class FeynmanTechniquePage(tk.Frame):
    """
    Interface for implementing the Feynman learning technique.

    The Feynman Technique page allows users to:
    - Input complex topics
    - Break down explanations
    - Identify knowledge gaps
    - Refine understanding
    """

    def __init__(self,
                 parent: Union[tk.Frame, tk.Tk],
                 controller: CodeBankApp = None) -> None:
        """
        Initialize Feynman technique interface.

        Args:
            parent: Parent tkinter window
            controller: Main application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.default_topic = "Matplotlib Style Change1"
        self.topic = self.default_topic
        self.sample_code, self.other_sample_code = fetch_code_snippet()

        self.gemini_client = GeminiClient()
        self._setup_ui()
        self._bind_events()
        logger.info("Feynman Technique page initialized")

    def set_code_info(self, code_info: CodebankEntry) -> None:
        """
        Set the code information and update the topic entry field.

        Args:
            code_info: CodebankEntry object containing title, exercise code,
                      and display code for the Feynman technique exercise

        Updates the sample topic from the title and sets the code samples
        for use in generating explanations.
        """
        self.topic = code_info.title
        self.sample_code, self.other_sample_code = (code_info.exercise_code,
                                                    code_info.display_code)
        self.topic_entry.delete(0, tk.END)
        self.topic_entry.insert(0, self.topic)

    def _setup_ui(self) -> None:
        """Configure and layout UI components."""
        self._create_title()
        self._create_topic_input()
        self._create_explanation_area()
        self._create_control_buttons()

    def _create_title(self) -> None:
        """Create and position page title."""
        self.title_label = tk.Label(
            self,
            text="Feynman Technique",
            font=("Arial", 18)
        )
        self.title_label.pack(pady=10, padx=10)

    def _create_topic_input(self) -> None:
        """Create topic input section."""
        self.topic_frame = ttk.LabelFrame(self, text="Topic")
        self.topic_frame.pack(fill="x", padx=10, pady=5)

        self.topic_entry = ttk.Entry(self.topic_frame)
        self.topic_entry.pack(fill="x", padx=5, pady=5)
        self.topic_entry.insert(0, self.topic)

    def _create_explanation_area(self) -> None:
        """Create explanation text area."""
        self.prompt_frame = ttk.Frame(self)
        self.prompt_frame.pack(fill="x", padx=10, pady=5)
        self.prompt_button = ttk.Button(
            self.prompt_frame,
            text="Generate Explanation",
            command=lambda: self._generate_explanation()
        )
        self.prompt_button.pack(side="left", padx=5)
        self.explanation_frame = ttk.LabelFrame(self, text="Explanation")
        self.explanation_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.explanation_text = scrolledtext.ScrolledText(
            self.explanation_frame,
            wrap=tk.WORD,
            height=10
        )
        self.explanation_text.pack(fill="both", expand=True, padx=5, pady=5)

    def _generate_explanation(self) -> None:
        """Generate explanation using Gemini API."""
        logger.info("Generating explanation...")
        self.explanation_text.config(state="disabled")
        explanation = self.gemini_client.explain_code(self.sample_code)
        self.explanation_text.config(state="normal")
        self.explanation_text.insert(tk.END, explanation)
        self.prompt_button.config(state="disabled")
        logger.info("Explanation generated")

    def _create_control_buttons(self) -> None:
        """Create control buttons."""
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("Save", self._save_explanation),
            ("Clear", self._clear_fields),
            ("Back to Home", lambda: self.controller.show_frame(HomePage))
        ]

        for text, command in buttons:
            ttk.Button(
                self.button_frame,
                text=text,
                command=command
            ).pack(side="left", padx=5)

    def _bind_events(self) -> None:
        """Bind keyboard and mouse events."""
        self.explanation_text.bind('<Control-s>',
                                   lambda e: self._save_explanation())
        self.explanation_text.bind('<Control-BackSpace>',
                                   lambda e: self._clear_fields())

    def _save_explanation(self) -> None:
        """Save the current explanation."""
        try:
            topic = self.topic_entry.get().strip()
            explanation = self.explanation_text.get("1.0", tk.END).strip()

            if not topic or not explanation:
                raise ValueError("Topic and explanation required")

            # Save implementation would go here
            logger.info(f"Explanation saved for topic: {topic}")
            messagebox.showinfo("Success", "Explanation saved successfully")

        except Exception as e:
            logger.error(f"Failed to save explanation: {str(e)}")
            messagebox.showerror("Error", "Failed to save explanation")

    def _clear_fields(self) -> None:
        """Clear all input fields."""
        self.topic_entry.delete(0, tk.END)
        self.prompt_button.config(state="normal")
        self.explanation_text.delete("1.0", tk.END)
        logger.debug("Fields cleared")


# Settings Page Class
class SettingsPage(tk.Frame):
    """
    Application settings interface.

    Manages user preferences including:
    - Theme settings
    - Font configurations
    - Integration settings
    """

    def __init__(self, parent: Union[tk.Frame, tk.Tk],
                 controller: CodeBankApp) -> None:
        """
        Initialize settings interface.

        Args:
            parent: Parent tkinter window
            controller: Main application controller
        """
        super().__init__(parent)
        self.controller = controller
        self._load_settings()
        self._setup_ui()
        logger.info("Settings page initialized")

    def _load_settings(self) -> None:
        """Load current application settings."""
        try:
            # Settings loading implementation would go here
            self.current_settings = {
                "theme": "light",
                "font_size": 12,
                "auto_save": True
            }
            logger.debug("Settings loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load settings: {str(e)}")
            self.current_settings = {}

    def _setup_ui(self) -> None:
        """Configure and layout UI components."""
        self._create_title()
        self._create_settings_controls()
        self._create_action_buttons()

    def _create_title(self) -> None:
        """Create and position page title."""
        tk.Label(
            self,
            text="Settings",
            font=("Arial", 18)
        ).pack(pady=10, padx=10)

    def _create_settings_controls(self) -> None:
        """Create settings control elements."""
        settings_frame = ttk.LabelFrame(self, text="Preferences")
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Theme selection
        self._create_theme_selector(settings_frame)

        # Font size control
        self._create_font_control(settings_frame)

        # Auto-save toggle
        self._create_auto_save_toggle(settings_frame)

    def _create_theme_selector(self,
                               parent: ttk.Frame | ttk.LabelFrame) -> None:
        """Create theme selection dropdown."""
        ttk.Label(parent, text="Theme:").pack(padx=5, pady=5)
        self.theme_var = tk.StringVar(value=self.current_settings.get("theme"))
        theme_combo = ttk.Combobox(
            parent,
            textvariable=self.theme_var,
            values=["light", "dark", "system"],
            state="readonly"
        )
        theme_combo.pack(padx=5, pady=5)

    @staticmethod
    def save_settings() -> None:
        """Save current settings configuration."""
        try:
            # Settings saving implementation would go here
            logger.info("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {str(e)}")
            messagebox.showerror("Error", "Failed to save settings")

    def _create_font_control(self, parent: ttk.Frame | ttk.LabelFrame) -> None:
        """Create font size adjustment controls."""
        ttk.Label(parent, text="Font Size:").pack(padx=5, pady=5)
        self.font_size_var = tk.IntVar(
            value=self.current_settings.get("font_size"))
        font_scale = ttk.Scale(
            parent, from_=8, to=24, variable=self.font_size_var)
        font_scale.pack(padx=5, pady=5)

    def _create_auto_save_toggle(self,
                                 parent: ttk.Frame | ttk.LabelFrame) -> None:
        """Create auto-save toggle switch."""
        self.auto_save_var = tk.BooleanVar(
            value=self.current_settings.get("auto_save"))
        ttk.Checkbutton(
            parent,
            text="Enable Auto-Save",
            variable=self.auto_save_var
        ).pack(padx=5, pady=5)

    def _validate_settings(self) -> bool:
        """
        Validate current settings configuration against acceptable ranges.

        Checks if:
        - Font size is between 8 and 24
        - (Other validations as needed)

        Returns:
            True if all settings are valid, False otherwise
        """
        try:
            font_size = self.font_size_var.get()
            if not (8 <= font_size <= 24):
                raise ValueError("Font size must be between 8 and 24")
            return True
        except Exception as e:
            logger.error(f"Settings validation failed: {str(e)}")
            return False

    def _create_action_buttons(self) -> None:
        """Create and position action buttons for settings management."""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)

        # Create action buttons
        buttons = [
            ("Save Settings", self.save_settings),
            ("Reset to Default", self._reset_to_default),
            ("Back to Home", lambda: self.controller.show_frame(HomePage))
        ]

        for text, command in buttons:
            ttk.Button(
                button_frame,
                text=text,
                command=command
            ).pack(side="left", padx=5)

    def _reset_to_default(self) -> None:
        """
        Reset all settings to default values.

        Resets to these defaults:
        - Theme: light
        - Font size: 12
        - Auto-save: enabled

        Updates both the internal settings state and the UI elements
        to reflect these default values.
        """
        try:
            default_settings = {
                "theme": "light",
                "font_size": 12,
                "auto_save": True
            }

            # Update UI elements with default values
            self.theme_var.set(default_settings["theme"])
            self.font_size_var.set(default_settings["font_size"])
            self.auto_save_var.set(default_settings["auto_save"])

            logger.info("Settings reset to default values")
            messagebox.showinfo("Success", "Settings reset to default values")
        except Exception as e:
            logger.error(f"Failed to reset settings: {str(e)}")
            messagebox.showerror("Error", "Failed to reset settings")
