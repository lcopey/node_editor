from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import List, Any
import sys


class ProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)

        self.excludes = list()

    def addExclusion(self, value):
        """Exclude item if `role` equals `value`

        Parameters
        ----------
        role:  int
            Qt role to compare `value` to
        value: Any
            Value to exclude

        Returns
        -------

        """
        self.excludes.append(value)
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        """Exclude items in `self.excludes`"""
        model = self.sourceModel()
        index = model.index(source_row, 0, QModelIndex())

        for value in self.excludes:
            data = model.data(index, 0)
            if data == value:
                return False

        return super(ProxyModel, self).filterAcceptsRow(
            source_row, source_parent)


class TableModel(QAbstractTableModel):
    def __init__(self, data: List[List]):
        super(TableModel, self).__init__()
        self._source_data = data
        self._data = data  # make a copy to handle filtering

    @property
    def source_data(self):
        return self._source_data

    # @source_data.setter
    # def source_data(self, new_value: List[List]):
    #     self._source_data = new_value

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """Overrides Qt's method and returns row count of the actual data

        Parameters
        ----------
        parent: QModelIndex

        Returns
        -------
        int
            row count
        """
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """Overrides Qt's method and returns column count of the actual data

        Parameters
        ----------
        parent: QModelIndex

        Returns
        -------
        int
            column count
        """
        return len(self._data[0])

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        """Overrides Qt's method and returns the data in the corresponding index

        Parameters
        ----------
        index: QModelIndex
            Holds row and column index
        role: int
            Corresponds to Qt role (Qt.DisplayRole, ...)

        Returns
        -------
        Any
            value at index
        """
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]


class TableView(QTableView):
    def __init__(self, data):
        super(TableView, self).__init__()
        self.dataModel = TableModel(data)
        # self.setModel(self.dataModel)

        self.proxyModel = ProxyModel()
        self.proxyModel.setSourceModel(self.dataModel)
        self.setModel(self.proxyModel)

        self.verticalHeader().hide()
        header = self.horizontalHeader()
        header.setSortIndicatorShown(True)
        self.setSortingEnabled(True)


if __name__ == '__main__':
    import random


    class MyWindow(QWidget):
        def __init__(self, data):
            super(MyWindow, self).__init__()
            self.filter_bar_1 = QLineEdit()
            self.filter_bar_2 = QLineEdit()
            self.filter_button = QPushButton()
            self.filter_button.setText('Filter')
            self.filter_button.clicked.connect(filter)
            self.table = TableView(data)

            innerLayout = QHBoxLayout()
            innerLayout.addWidget(self.filter_bar_1)
            innerLayout.addWidget(self.filter_bar_2)
            innerLayout.addWidget(self.filter_button)

            layout = QVBoxLayout()
            layout.addLayout(innerLayout)
            layout.addWidget(self.table)
            self.setLayout(layout)

    def filter():
        try:
            value = wnd.filter_bar_1.text()
            if value != '':
                value = int(value)
                print('filter', value)
                model = wnd.table.model()
                model.addExclusion(value)
        except Exception as e:
            print(e)


    app = QApplication(sys.argv)

    data = [[random.randint(0, 10) for i in range(3)] for j in range(100)]
    wnd = MyWindow(data)
    wnd.show()
    # table = TableView(data)
    # table.show()

    sys.exit(app.exec_())
