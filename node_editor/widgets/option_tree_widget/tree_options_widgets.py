import sys
from PyQt5.QtWidgets import *
from draggable_list_widget import *
from tree_options import OptionTreeWidget


class PivotOptionTree(OptionTreeWidget):
    def __init__(self):
        super(PivotOptionTree, self).__init__(names=['pivot'], acceptDrops=True)
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
        for value in ['rows', 'columns', 'values']:
            self.addRootItem(itemName=value, flags=flags)

        self.registerDropValidator()


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
            self.optionTree = PivotOptionTree()
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
