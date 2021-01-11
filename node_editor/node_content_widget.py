# -*- encoding: utf-8 -*-
"""A module containing base class for Node's content graphical representation. It also contains examples of
overriden Text widget which can pass it's parent notification about currently being modified."""
from collections import OrderedDict
from node_editor.node_serializable import Serializable
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeyEvent, QFocusEvent
from .utils import dumpException


class NodeContentWidget(QWidget, Serializable):
    """Class docs"""

    def __init__(self, node: 'Node', parent: QWidget = None):
        """Default constructor

        Parameters
        ----------
        node : Node
            :py:class:`~node_editor.node_node.Node` currently holding the content.
        parent : QWidget
            parent widget in which the content is displayed
        """
        self.node = node
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """Setting up layout"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some _title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QNETextEdit("foo"))

    def setEditingFlag(self, value: bool):
        """Set the editing flag from the GraphicalView"""
        self.node.scene.getView().editingFlag = value

    def serialize(self) -> OrderedDict:
        """Default serialization method.

        To be overriden by user.

        Returns
        -------
        ``OrderedDict``

        """
        return OrderedDict([
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        """Default deserialize method.

        To be overriden by user.

        Parameters
        ----------
        data : ``dict``
            data used to deserialize
        hashmap : ``dict``
            hashmap containing connection between nodes, edges

        Returns
        -------
        ``bool``
            - True if sucessful
            - False if failed
        """
        return True


class QNETextEdit(QTextEdit):
    def focusInEvent(self, event: QFocusEvent):
        try:
            self.parentWidget().setEditingFlag(True)
            super().focusInEvent(event)
        except Exception as e:
            dumpException(e)

    def focusOutEvent(self, event: QFocusEvent):
        try:
            self.parentWidget().setEditingFlag(False)
            super().focusOutEvent(event)
        except Exception as e:
            dumpException(e)
