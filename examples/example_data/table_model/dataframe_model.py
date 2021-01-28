import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from node_editor.utils import dumpException
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QHeaderView, QTableView


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

    def __init__(self, view: 'QTableView', dataframe: pd.DataFrame, editable=False):
        """

        Parameters
        ----------
        view : QTableView
            Reference to QTableView holding the model
        dataframe
        editable
        """
        QAbstractTableModel.__init__(self)
        # Reference to initial dataframe
        self.view = view
        self._source_data = dataframe
        # Copy of the dataframe to handle filtering
        self._data = self._source_data
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
            self._source_data.iloc[index.row(), index.column()] = value
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
        """Rename columns or index section.

        Parameters
        ----------
        section : int
            position of the index to rename
        orientation : Qt.Orientation
            Qt.Horizontal to rename column, Qt.Vertical to rename index
        value : Any
            New value for column or index section
        """
        if orientation == Qt.Horizontal:
            columns = self._data.columns.values.copy()
            columns[section] = value
            self._data.columns = columns

        if orientation == Qt.Vertical:
            index = self._data.index.values.copy()
            index[section] = value
            self._data.index = index

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        """Sort the undelying dataframe

        Parameters
        ----------
        column : int
            Column along which to sort
        order : Qt.SortOrder
            Ascending or descending
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(self._data.columns[column], ascending=not order)
            self.layoutChanged.emit()

        except Exception as e:
            dumpException(e)

    def filter(self):
        """Filter the underlying dataframe

        Parameters
        ----------
        header : QHeaderView
            reference to header holding the text for filtering

        """
        try:
            header = self.view.horizontalHeader()
            mask = None
            self.layoutAboutToBeChanged.emit()
            # Filter according to filter text in header
            # TODO handle in function of datatype
            for i in range(self.columnCount()):
                text = header.getFilterTextAtIndex(i)
                column = self._source_data.columns[i]
                if text != '':
                    if mask is not None:
                        mask &= self._source_data[column].str.contains(text, na=False)
                    else:
                        mask = self._source_data[column].str.contains(text, na=False)

            if mask is None:
                self._data = self._source_data
            else:
                self._data = self._source_data[mask]

            self.layoutChanged.emit()

        except Exception as e:
            dumpException(e)
