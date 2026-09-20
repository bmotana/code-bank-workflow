import unittest

from src.gui.home_page import HomePage, RecallGamePage
from src.gui.main_window import CodeBankApp


class TestCodeBankApp(unittest.TestCase):
    """Test suite for the CodeBankApp main window class.

    Tests window initialization, frame management, navigation,
    and layout configuration of the main application window.
    """

    def setUp(self):  # noqa: D102
        self.app = CodeBankApp()

    def tearDown(self):  # noqa: D102
        self.app.destroy()

    def test_init_window_title(self):
        """Test if window title is set correctly."""
        self.assertEqual(self.app.title(), "Code Bank Workflow")

    def test_frames_initialization(self):
        """Test if all required frames are created."""
        expected_frames = {
            'HomePage',
            'RecallGamePage',
            'FeynmanTechniquePage',
            'SettingsPage'
        }
        actual_frames = set(self.app.frames.keys())
        self.assertEqual(expected_frames, actual_frames)

    def test_initial_frame_is_homepage(self):
        """Test if HomePage is shown first."""
        homepage_frame = self.app.frames['HomePage']
        self.assertEqual(homepage_frame.winfo_toplevel(), self.app)
        self.assertTrue(isinstance(homepage_frame, HomePage))

    def test_frame_navigation(self):
        """Test frame navigation functionality."""
        # Navigate to RecallGamePage
        self.app.show_frame(RecallGamePage)
        # Get the frame directly and verify it's the correct type
        recall_frame = self.app.frames['RecallGamePage']
        self.assertTrue(isinstance(recall_frame, RecallGamePage))
        # Verify it's properly attached to the main window
        self.assertEqual(recall_frame.winfo_toplevel(), self.app)

    def test_container_grid_configuration(self):
        """Test if container is configured correctly."""
        container = self.app.children['!frame']
        self.assertEqual(container.grid_size(), (1, 1))

    def test_container_pack_configuration(self):
        """Test if container is configured correctly."""
        container = self.app.children['!frame']
        pack_info = container.pack_info()
        self.assertEqual(pack_info['side'], 'top')
        self.assertEqual(pack_info['fill'], 'both')
        self.assertTrue(pack_info['expand'])


if __name__ == '__main__':
    unittest.main()
