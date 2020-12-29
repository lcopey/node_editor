from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QNEDragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()

    def addMyItems(self):
        self.addMyItem("Input", "icons/in.png")
        self.addMyItem("Output", "icons/out.png")
        self.addMyItem("Add", "icons/add.png")
        self.addMyItem("Subtract", "icons/sub.png")
        self.addMyItem("Multiply", "icons/mul.png")
        self.addMyItem("Divide", "icons/divide.png")

    def addMyItem(self, name, icon=None, op_code=0):
        # initialize QListWidgetItem
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(icon if icon is not None else '.')
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)
