import unittest
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from data_node_editor import DataWindow

app = QApplication(sys.argv)


class TestDataNodeEditor(unittest.TestCase):
    def setUp(self) -> None:
        # Lanch the application

        app.setStyle('Fusion')
        self.wnd = DataWindow()
        self.wnd.show()
        self.wnd.onFileNew()

    def test_data_node_actions(self):
        # Test
        current_area = self.wnd.getCurrentNodeEditorWidget()
        QTest.mouseClick(current_area, Qt.RightButton)


if __name__ == '__main__':
    unittest.main()
