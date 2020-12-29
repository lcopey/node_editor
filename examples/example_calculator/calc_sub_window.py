from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from node_editor.node_editor_widget import NodeEditorWidget


class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()
        self.scene.addHasBeenModifiedListener(self.setTitle)

        self._close_event_listeners = []

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def closeEvent(self, event: QCloseEvent) -> None:
        print('Calculator closeEvent')

    def addCloseEventListener(self, callback: 'function'):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners:
            callback(self, event)
