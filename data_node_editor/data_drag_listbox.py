import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Optional
from node_editor.utils import dumpException, get_path_relative_to_file
from .data_conf import *


class DragListBox(QListWidget):
    """Class implementing a list of available :class:'~data_node_base.DataNode'"""

    def __init__(self, parent: Optional[QWidget] = None):
        """Instantiates :class:'~data_drag_listbox.rst.DragListBox'

        Subclass QListWidget to implement specific drag features creating nodes when dropping on a
        :class:'~data_subwindow.DataSubWindow'
        Parameters
        ----------
        parent: Optional[QWidget]
            Parent widget
        """
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()

    def addMyItems(self):
        """Add itmes from DATA_NODES in the current QListWidget"""
        keys = NodeFactory.get_nodes()
        keys.sort()

        for key in keys:
            node = NodeFactory.from_op_code(key)
            self.addMyItem(node.op_title, node.icon, node.getOpCode())

    def addMyItem(self, name: str, icon: str = None, op_code: str = ''):
        """Helper function adding item to the current ListWidget

        Parameters
        ----------
        name : str
            name displayed
        icon : str
            path to the icon
        op_code : int
            id of the item
        """
        # initialize QListWidgetItem
        item = QListWidgetItem(name, self)
        # look for resources
        icon_path = icon
        if not os.path.exists(icon):
            icon_path = get_path_relative_to_file(__file__, icon)
        if not os.path.exists(icon_path):
            icon_path = None

        pixmap = QPixmap(icon_path if icon_path is not None else '.')
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))
        # item.setText(name)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
        # setup data
        item.setData(Qt.UserRole, pixmap)  # store pixmap at position Qt.UseRole
        item.setData(Qt.UserRole + 1, op_code)  # store op_code at position Qt.UserRole + 1

    def startDrag(self, *args, **kwargs):
        """Initiates drag object"""
        try:
            # Retrieve the operational code
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)
            # name = item.text()

            # Define Mime data
            # Retrieve pixmap
            pixmap = QPixmap(item.data(Qt.UserRole))
            # Populate a QByteArray with datastream
            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeQString(op_code)
            dataStream.writeQString(item.text())

            # instantiate mime data of LISTBOX_MIMETYPE type
            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)  # set pixmap to drag
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))  # Hotspot in the middle of the drag

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dumpException(e)
