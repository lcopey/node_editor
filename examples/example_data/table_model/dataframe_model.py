import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtWidgets import QTableView, QHeaderView
from typing import Any


def _align(value):
    if pd.api.types.is_numeric_dtype(value):
        return Qt.AlignVCenter + Qt.AlignRight
    else:
        return Qt.AlignVCenter + Qt.AlignLeft


class DataframeModel(QAbstractTableModel):
    """Class representing a pandas DataFrame in a Qt context"""

    def __init__(self, dataframe: pd.DataFrame, editable=False):
        QAbstractTableModel.__init__(self)
        self._data = dataframe
        self.editable = editable

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        """Internal method to QAbstractTableModel overridden to supply information on the header

        Parameters
        ----------
        index
        role

        Returns
        -------

        """
        if index.isValid():
            value = self._data.iloc[index.row(), index.column()]
            if role == Qt.DisplayRole:
                if pd.isna(value):
                    return ''
                return str(value)
            elif role == Qt.TextAlignmentRole:
                return _align(value)
            # elif role == Qt.DecorationRole

        return None

    def flags(self, index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if self.editable:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        # Set value in case of editable
        if role == Qt.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            return True

    @property
    def dataframe(self):
        return self._data

    def headerData(self, p_int: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = None):
        """Internal method to QAbstractTableModel overridden to supply information on the header

        Parameters
        ----------
        p_int : int
            index of the column or index requested
        orientation : Qt.Orientation
        role : Qt.ItemDataRole

        Returns
        -------
        str

        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[p_int]
            if orientation == Qt.Vertical:
                return self._data.index[p_int]
        return None


class DataframeView(QTableView):
    """Class representing a view of a :class:`~DataFrameModel`"""

    def __init__(self, parent=None, dataframe: pd.DataFrame = None, editable=False):
        super(DataframeView, self).__init__(parent)
        # header = MyHeader()
        # self.setHorizontalHeader(QHeaderView(Qt.Horizontal))
        self.horizontalHeader().setSectionsMovable(True)
        self.verticalHeader().setSectionsMovable(True)
        self.editable = editable
        if dataframe is not None:
            self.setDataFrame(dataframe, editable=self.editable)

    def setDataFrame(self, dataframe: pd.DataFrame, editable=False):
        """Define the dataframe through a new `DataframeModel`

        Parameters
        ----------
        dataframe : pd.DataFrame
            dataframe holding the data
        editable : bool
            flag setting the `DataframeModel` as editable
        """
        dataframe_model = DataframeModel(dataframe=dataframe, editable=editable)
        super().setModel(dataframe_model)

    def getDataFrame(self):
        """Returns dataframe currently hold in the `DataframeModel`

        Returns
        -------
        pd.DataFrame
            dataframe currently hold in the `DataframeModel`
        """
        return self.model().dataframe
