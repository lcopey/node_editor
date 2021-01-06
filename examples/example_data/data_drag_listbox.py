from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from node_editor.utils import dumpException
from .data_conf import *


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
        keys = list(DATA_NODES.keys())
        keys.sort()
        for key in keys:
            node = get_call_from_opcode(key)
            self.addMyItem(node.op_title, node.icon, node.op_code)

    def addMyItem(self, name: str, icon: str = None, op_code: int = 0):
        """Helper function adding item to the current ListWidget

        Parameters
        ----------
        name : str
            name displayed
        icon : str
            path to the icon
        op_code : int
            id of the item

        Returns
        -------
        None

        """
        # initialize QListWidgetItem
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(icon if icon is not None else '.')
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))
        # item.setText(name)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
        # setup data
        item.setData(Qt.UserRole, pixmap)  # store pixmap at position Qt.UseRole
        item.setData(Qt.UserRole + 1, op_code)  # store op_code at position Qt.UserRole + 1

    def startDrag(self, *args, **kwargs):
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
            dataStream.writeInt(op_code)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)  # set pixmap to drag
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))  # Hotspot in the middle of the drag

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dumpException(e)
