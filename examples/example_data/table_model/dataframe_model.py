import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from node_editor.utils import dumpException
from typing import Any


def _align(value: Any) -> Qt.AlignmentFlag:
    """Align values in the `DataframeModel` according to their type

    Parameters
    ----------
    value: Any
        value to align

    Returns
    -------
    Qt.AlignmentFlag
    """
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

    def flags(self, index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if self.editable:
            flags |= Qt.ItemIsEditable
        return flags

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
                return str(self._data.columns[p_int])
            if orientation == Qt.Vertical:
                return str(self._data.index[p_int])

        return None

    def setHeaderValue(self, section: int, orientation: Qt.Orientation, value: Any):
        if orientation == Qt.Horizontal:
            columns = self._data.columns.values.copy()
            columns[section] = value
            self._data.columns = columns

        if orientation == Qt.Vertical:
            index = self._data.index.values.copy()
            index[section] = value
            self._data.index = index

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(self._data.columns[column], ascending=not order)
            self.layoutChanged.emit()

        except Exception as e:
            dumpException(e)
