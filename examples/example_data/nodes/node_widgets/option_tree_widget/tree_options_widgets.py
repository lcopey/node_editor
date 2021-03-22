import sys
from PyQt5.QtWidgets import *
from draggable_list_widget import *
from tree_options import OptionTreeWidget


class PivotOptionTree(OptionTreeWidget):
    def __init__(self):
        super(PivotOptionTree, self).__init__(names=['pivot'], acceptDrops=True)
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
        for n, value in enumerate(['rows', 'columns', 'values']):
            self.addRootItem(itemName=value, flags=flags)
        self.expandAll()

        self.registerDropValidator(PivotOptionTree.isRootChildItem)

    def isRootChildItem(self, source, destination, item) -> bool:
        """Check wether the item is dropped on first level of items.

        Parameters
        ----------
        source :
            source widget of the item
        destination :
            destination widget or item where to drop
        item :
            item to drop in destination

        Returns
        -------
        bool
            True to validate the move, False otherwise

        """
        root = self.invisibleRootItem()
        child = [root.child(n) for n in range(root.childCount())]
        return destination in child


class ResetIndexOptionTree(OptionTreeWidget):
    def __init__(self):
        super(ResetIndexOptionTree, self).__init__(names=['reset_index', 'options'])
        dropDown = QComboBox()
        dropDown.addItems(['index', 'column'])
        self.addRootItem('axis', dropDown)


class StackOptionTree(OptionTreeWidget):
    def __init__(self):
        super(StackOptionTree, self).__init__(names=['stack', 'options'])
        dropDown = QComboBox()
        dropDown.addItems(['index', 'column'])
        self.addRootItem('axis', dropDown)


if __name__ == '__main__':
    app = QApplication(sys.argv)


    class MyWidget(QWidget):
        def __init__(self):
            super(MyWidget, self).__init__()
            self.sourceList = DraggableListWidget()
            self.sourceList.addItems([value for value in range(10)])
            # self.optionTree = OptionTreeWidget(['func', 'options'])
            # self.optionTree = PivotOptionTree()
            # self.optionTree = ResetIndexOptionTree()
            self.optionTree = StackOptionTree()
            layout = QVBoxLayout()
            layout.addWidget(self.sourceList)
            layout.addWidget(self.optionTree)
            self.setLayout(layout)


    # optionTree = OptionTreeWidget(names=['rename', 'options'])
    # dropDown = QComboBox()
    # dropDown.addItems(['index', 'column'])
    # optionTree.addRootItem('axis', dropDown)
    # optionTree.show()
    wdg = MyWidget()
    wdg.show()

    sys.exit(app.exec_())
