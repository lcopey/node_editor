from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import List, Any
import sys


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

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.dataModel)
        self.setModel(self.proxyModel)

        self.verticalHeader().hide()
        header = self.horizontalHeader()
        header.setSortIndicatorShown(True)
        self.setSortingEnabled(True)


if __name__ == '__main__':
    import random


    app = QApplication(sys.argv)

    data = [[random.randint(0, 10) for i in range(3)] for j in range(100)]
    table = TableView(data)
    table.show()

    sys.exit(app.exec_())
