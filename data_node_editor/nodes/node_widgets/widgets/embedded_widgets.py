import sys
from PyQt5.QtWidgets import QWidget, QListWidget, QTreeWidget, QListWidgetItem, QComboBox, QApplication
from typing import Optional, Union, Any


class EmbeddedListWidget(QListWidget):
    def __init__(self, parent=None, widget: Optional[QWidget] = None):
        super(EmbeddedListWidget, self).__init__(parent)
        self.widget = widget

    def addItem(self, aitem: QListWidgetItem) -> None:
        super(EmbeddedListWidget, self).addItem(aitem)
        self.setItemWidget(aitem, self.widget)


class EmbeddedTreeWidget(QTreeWidget):
    def __init__(self, parent=None, widget: Optional[QWidget] = None):
        super(EmbeddedTreeWidget, self).__init__(parent)
        self.widget = widget
        

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        cmb = QComboBox()
        cmb.addItems(['option 1', 'option 2', 'option 3'])

        wdg = EmbeddedListWidget(widget=cmb)
        wdg.addItem(QListWidgetItem('Item 1'))

        wdg.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(e)
