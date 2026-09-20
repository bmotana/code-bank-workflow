"""
Unit tests for the home page GUI components.

Tests cover:
- HomePage navigation and button functionality
- RecallGamePage mechanics and game flow
- FeynmanTechniquePage input handling and validation
- SettingsPage configuration and validation
"""

import tkinter as tk
import unittest
from tkinter import ttk
from typing import cast
from unittest.mock import MagicMock, patch
from unittest.mock import Mock

from src.gui.home_page import (
    FeynmanTechniquePage,
    HomePage,
    RecallGamePage,
    SettingsPage
)
from src.gui.my_types import CodeBankApp


class TestRecallPage(unittest.TestCase):
    """Test suite for RecallPage functionality and initialization."""

    def setUp(self):  # noqa: D102
        self.root = tk.Tk()
        self.controller = cast(CodeBankApp,
                               Mock(spec=CodeBankApp))
        self.recall_game_page = RecallGamePage(self.root,
                                               self.controller)

    def tearDown(self):  # noqa: D102
        self.root.destroy()

    def test_sample_code_retrieval(self):
        """Test navigation button handlers trigger frame changes."""
        self.assertIsInstance(self.recall_game_page.exercise_code_lines, tuple)
        self.assertNotEqual(self.recall_game_page.display_code, "")


class TestHomePage(unittest.TestCase):
    """Test suite for HomePage navigation and button functionality."""

    def setUp(self):  # noqa: D102
        self.root = tk.Tk()
        self.controller = cast(CodeBankApp,
                               MagicMock(autospec=True, spec=CodeBankApp))
        self.home_page = HomePage(self.root, self.controller)

    def tearDown(self):  # noqa: D102
        self.root.destroy()

    def test_init_creates_navigation_buttons(self):
        """Verify HomePage creates required navigation buttons on init."""
        print(self.home_page.winfo_children())
        buttons = [widget for widget in self.home_page.winfo_children()
                   if isinstance(widget, ttk.Button)]
        self.assertGreaterEqual(len(buttons), 3)

    def test_navigation_button_commands(self):
        """Check sample code retrieval and storage format."""
        self.home_page._create_navigation_buttons()
        self.controller.show_frame.assert_not_called()
        buttons = [widget for widget in self.home_page.winfo_children()
                   if isinstance(widget, ttk.Button)]
        buttons[0].invoke()
        self.controller.show_frame.assert_called_once()


class TestRecallGamePage(unittest.TestCase):
    """Test suite for RecallGamePage game mechanics and user interactions."""

    def setUp(self):  # noqa: D102
        self.root = tk.Tk()
        self.controller = cast(CodeBankApp,
                               Mock(spec=CodeBankApp))
        self.game_page = RecallGamePage(self.root, self.controller)

    def tearDown(self):  # noqa: D102
        self.root.destroy()

    def test_initialize_code_sets_sample_code(self):
        """Test code initialization sets sample code correctly."""
        with patch('src.gui.home_page.send_code_snippet') as mock_send:
            mock_send.return_value = ("test code", ["line1", "line2"])
            self.game_page._initialize_code()
            self.assertEqual(self.game_page.display_code, "test code")
            self.assertEqual(self.game_page.exercise_code_lines,
                             ["line1", "line2"])

    @patch('tkinter.messagebox.showinfo')
    def test_check_game_completed(self, mock_showinfo: MagicMock):
        """Test game completion logic and victory message display."""
        self.game_page.exercise_code_lines = ["test line"]
        self.game_page.current_level = 1
        answer = "test line"
        self.game_page.answer_input.insert("1.0", answer)
        self.game_page._check_answer()
        mock_showinfo.assert_called_once_with(
            "Game Over",
            "Congratulations! You've completed all levels.")
        # self.assertEqual(self.game_page.current_level, 2)

    def test_check_answer_correct(self):
        """Verify correct answer handling and level progression."""
        self.game_page.exercise_code_lines = ["test line", "test line 2"]
        self.game_page.current_level = 1
        answer = "test line"
        self.game_page.answer_input.insert("1.0", answer)
        self.game_page._check_answer()
        self.assertEqual(self.game_page.current_level, 2)

    def test_check_answer_incorrect(self):
        """Test incorrect answer handling and level maintenance."""
        self.game_page.exercise_code_lines = ["test line"]
        self.game_page.current_level = 1
        self.game_page.answer_input.insert("1.0", "wrong answer")
        initial_level = self.game_page.current_level
        self.game_page._check_answer()
        self.assertEqual(self.game_page.current_level, initial_level)


class TestFeynmanTechniquePage(unittest.TestCase):
    """Tests for FeynmanTechniquePage input handling."""

    def setUp(self):  # noqa: D102
        self.root = tk.Tk()
        self.controller = cast(CodeBankApp,
                               Mock(spec=CodeBankApp))
        self.feynman_page = FeynmanTechniquePage(self.root, self.controller)

    def tearDown(self):  # noqa: D102
        self.root.destroy()

    def test_clear_fields(self):
        """Verify clearing fields removes all user input."""
        self.feynman_page.topic_entry.insert(0, "test topic")
        self.feynman_page.explanation_text.insert("1.0", "test explanation")
        self.feynman_page._clear_fields()
        self.assertEqual(self.feynman_page.topic_entry.get(), "")
        self.assertEqual(
            self.feynman_page.explanation_text.get("1.0", tk.END).strip(),
            ""
        )

    def test_save_explanation_empty_fields(self):
        """Test error handling for saving empty input fields."""
        # Setup empty fields
        self.feynman_page.topic_entry.delete(0, tk.END)
        self.feynman_page.explanation_text.delete("1.0", tk.END)

        # Mock messagebox to capture error
        with patch('tkinter.messagebox.showerror') as mock_error:
            self.feynman_page._save_explanation()
            mock_error.assert_called_once()


class TestSettingsPage(unittest.TestCase):
    """Test suite for SettingsPage configuration handling and validation."""

    def setUp(self):  # noqa: D102
        self.root = tk.Tk()
        self.controller = cast(CodeBankApp,
                               Mock(spec=CodeBankApp))
        self.settings_page = SettingsPage(self.root, self.controller)

    def tearDown(self):  # noqa: D102
        self.root.destroy()

    def test_load_settings_defaults(self):
        """Verify default settings are loaded with correct initial values."""
        self.assertEqual(self.settings_page.current_settings["theme"], "light")
        self.assertEqual(self.settings_page.current_settings["font_size"], 12)
        self.assertTrue(self.settings_page.current_settings["auto_save"])

    def test_reset_to_default(self):
        """Verify settings reset restores default values."""
        self.settings_page.theme_var.set("dark")
        self.settings_page.font_size_var.set(18)
        self.settings_page.auto_save_var.set(False)
        self.settings_page._reset_to_default()
        self.assertEqual(self.settings_page.theme_var.get(), "light")
        self.assertEqual(self.settings_page.font_size_var.get(), 12)
        self.assertTrue(self.settings_page.auto_save_var.get())

    def test_validate_settings_valid_font(self):
        """Test settings validation with valid font size input."""
        self.settings_page.font_size_var.set(14)
        self.assertTrue(self.settings_page._validate_settings())

    def test_validate_settings_invalid_font(self):
        """Verify settings validation correctly rejects invalid font sizes."""
        self.settings_page.font_size_var.set(30)
        self.assertFalse(self.settings_page._validate_settings())


if __name__ == '__main__':
    unittest.main()
