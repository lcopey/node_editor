import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QTableView, QHeaderView


def _align(value):
    if pd.api.types.is_numeric_dtype(value):
        return Qt.AlignVCenter + Qt.AlignRight
    else:
        return Qt.AlignVCenter + Qt.AlignLeft


class DataframeModel(QAbstractTableModel):
    """Class representing a pandas DataFrame in a Qt context"""

    def __init__(self, dataframe: pd.DataFrame):
        QAbstractTableModel.__init__(self)
        self._data = dataframe

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
                return str(value)
            elif role == Qt.TextAlignmentRole:
                return _align(value)
            # elif role == Qt.DecorationRole

        return None

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
    def __init__(self, parent=None, dataframe: pd.DataFrame = None):
        super(DataframeView, self).__init__(parent)
        # header = MyHeader()
        # self.setHorizontalHeader(QHeaderView(Qt.Horizontal))
        self.horizontalHeader().setSectionsMovable(True)
        self.verticalHeader().setSectionsMovable(True)
        if dataframe is not None:
            self.setDataFrame(dataframe)

    def setDataFrame(self, dataframe: pd.DataFrame):
        dataframe_model = DataframeModel(dataframe=dataframe)
        super().setModel(dataframe_model)
