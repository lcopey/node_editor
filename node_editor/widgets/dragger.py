from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from typing import Union, List


class Dragger(QWidget):
    def __init__(self, fromListLabel: str = 'Input', toListNames: Union[List[str], None] = None):
        super().__init__()
        # Define source list
        self.sourceListLbl = QLabel(fromListLabel)
        self.sourceList = QListWidget()
        self.sourceList.setDragDropMode(QListWidget.DragDrop)
        self.sourceList.setSelectionMode(QListWidget.ExtendedSelection)
        self.sourceList.setDefaultDropAction(Qt.MoveAction)
        # self.sourceList.setAcceptDrops(True)

        # Define destination tree
        self.toTree = QTreeWidget()
        self.toTree.header().hide()
        self.toTree.setDragDropMode(QListWidget.DragDrop)
        self.toTree.setSelectionMode(QListWidget.ExtendedSelection)
        self.toTree.setDefaultDropAction(Qt.MoveAction)

        root = self.toTree.invisibleRootItem()
        root.setFlags(Qt.NoItemFlags)
        if toListNames is None:
            toListNames = ['output']
        for name in toListNames:
            item = QTreeWidgetItem(root)
            item.setText(0, name)
            item.setExpanded(True)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.sourceListLbl)
        self.layout.addWidget(self.sourceList)
        self.layout.addWidget(self.toTree)
        self.setLayout(self.layout)

    def addSourceItems(self, itemNames: List[str]):
        for name in itemNames:
            item = QListWidgetItem()
            item.setText(name)
            self.sourceList.addItem(item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dragger = Dragger(toListNames=['output_1', 'output_2'])
    dragger.addSourceItems(['input{}'.format(n) for n in range(10)])
    dragger.show()
    sys.exit(app.exec_())
