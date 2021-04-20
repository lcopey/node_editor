import sys
from PyQt5.QtWidgets import QWidget, QListWidget, QTreeWidget, QListWidgetItem, QTreeWidgetItem, QComboBox, QApplication
from PyQt5.QtCore import Qt
from typing import Optional, List, Union, Any


class ComboBoxOptionItem(QComboBox):
    def __init__(self, parent=None, options: Optional[List[str]] = None):
        super(ComboBoxOptionItem, self).__init__(parent)
        if options:
            self.addItems(options)


class EmbeddedListWidget(QListWidget):
    def __init__(self, parent=None, defaultWidget: Optional[QWidget] = None):
        super(EmbeddedListWidget, self).__init__(parent)
        self.defaultWidget = defaultWidget

    def addItem(self, itemName: str, widget: Optional[QWidget] = None) -> None:
        item = QListWidgetItem()
        item.setText(itemName)
        super(EmbeddedListWidget, self).addItem(item)
        if widget is None:
            widget = self.widget
        self.setItemWidget(item, widget)


class EmbeddedTreeWidget(QTreeWidget):
    def __init__(self, parent=None, headers: Optional[List[str]] = None, defaultWidget: Optional[QWidget] = None):
        super(EmbeddedTreeWidget, self).__init__(parent)
        self.setColumnCount(2)
        if headers:
            self.setHeaderLabels(headers)
        self.widget = defaultWidget
        self.widget.setParent(self)

    def addRootItem(self, itemName: str, widget: Optional[QWidget] = None,
                    flags: Optional[Qt.ItemFlag] = None):
        root = self.invisibleRootItem()

        item = QTreeWidgetItem()
        item.setText(0, itemName)
        if flags:
            item.setFlags(flags)
        root.addChild(item)

        if widget is None:
            widget = self.defaultWidget
        else:
            widget.setParent(self)
        if widget:
            self.setItemWidget(item, 1, widget)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        cmb = ComboBoxOptionItem(options=['option 1', 'option 2', 'option 3'])

        cmb2 = QComboBox()
        cmb2.addItems(['test1', 'test2'])

        wdg = EmbeddedTreeWidget(defaultWidget=cmb, headers=['options', 'value'])
        wdg.addRootItem('Item 1', widget=cmb)

        wdg.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(e)
