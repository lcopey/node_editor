from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from node_editor.utils import dumpException
from .calc_conf import *


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
        self.addMyItem("Input", "icons/in.png", OP_NODE_INPUT)
        self.addMyItem("Output", "icons/out.png", OP_NODE_OUTPUT)
        self.addMyItem("Add", "icons/add.png", OP_NODE_ADD)
        self.addMyItem("Subtract", "icons/sub.png", OP_NODE_SUB)
        self.addMyItem("Multiply", "icons/mul.png", OP_NODE_MUL)
        self.addMyItem("Divide", "icons/divide.png", OP_NODE_DIV)

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
        print('Listbox::startDrag')
        try:
            # Retrieve the operational code
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)
            # name = item.text()
            print('Dragging item', op_code, item)

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
