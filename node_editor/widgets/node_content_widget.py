from collections import OrderedDict
from node_editor.node_serializable import Serializable
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeyEvent, QFocusEvent


class QNENodeContentWidget(QWidget, Serializable):
    def __init__(self, node, parent=None):
        self.node = node
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some _title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QNETextEdit("foo"))

    def setEditingFlag(self, value):
        # TODO refaire avec une fonction dans QNEGraphicsView
        self.node.scene.grScene.views()[0].editingFlag = value

    def serialize(self):
        return OrderedDict([

        ])

    def deserialize(self, data, hashmap={}):
        return False


class QNETextEdit(QTextEdit):
    def focusInEvent(self, event: QFocusEvent):
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
