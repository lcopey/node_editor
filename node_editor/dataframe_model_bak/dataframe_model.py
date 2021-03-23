import re
import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from node_editor.utils import dumpException
from typing import Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QHeaderView, QTableView

TYPE_OPTIONS = ['str', 'int', 'float', 'bool']


def _align(value: Any) -> Qt.AlignmentFlag:
    """Align values in the `DataTableModel` according to their type

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

    def __init__(self, view: 'QTableView', dataframe: Union[pd.DataFrame, pd.Series], editable=False,
                 columnDecorator: bool = True):
        """Initiate a new `DataTableModel`, base class for representing the data.

        Parameters
        ----------
        view : QTableView
            Reference to QTableView holding the model
        dataframe : pd.DataFrame or pd.Series
            DataFrame or Series as source for the model
        editable : bool
            if ``True`` set the model as editable by adding a delegate
        """
        super().__init__()
        # Reference to initial dataframe
        self.view = view
        self.dataframe = dataframe
        self.isDataFrame = isinstance(self._data, pd.DataFrame)
        self.editable = editable
        self.columnDecorator = columnDecorator
        self._type_icons = {key: QIcon('./resources/{}_icon.svg'.format(key)) for key in TYPE_OPTIONS}

    def flags(self, index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if self.editable:
            flags |= Qt.ItemIsEditable
        return flags

    def rowCount(self, parent=None):
        if self._data is not None:
            return self._data.shape[0]
        else:
            return 0

    def columnCount(self, parent=None):
        if self.isDataFrame:
            return self._data.shape[1]
        else:
            return 1

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        """Internal method to QAbstractTableModel overridden to supply information on the header

        Returns value corresponding to index.
        Implements :
            - Qt.DisplayRole
            - Qt.TextAlignmentRole
        Overrides to implement :
            - Qt.DecorationRole
        """
        if index.isValid():
            if self.isDataFrame:
                value = self._data.iloc[index.row(), index.column()]
            else:
                value = self._data.iloc[index.row()]

            if role == Qt.DisplayRole:
                # Need to check type since a cell might contain a list or Series, then .isna returns a Series not a bool
                cell_is_na = pd.isna(value)
                if type(cell_is_na) == bool and cell_is_na:
                    return ""
                return str(value)
            elif role == Qt.TextAlignmentRole:
                return _align(value)

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        """Assign value to the cell index of the table

        Parameters
        ----------
        index : QModelIndex
            index (row, column) of the table to change
        value : Any
            New to assign to index
        role : int
            Qt Role, usually Qt.EditRole

        Returns
        -------
        ``bool``
            ``True```in case of succes

        """
        # Set value in case of editable
        if role == Qt.EditRole:
            if self.isDataFrame:
                self._source_data.iloc[index.row(), index.column()] = value
            else:
                self._source_data.iloc[index.row()] = value
            return True

    @property
    def dataframe(self):
        return self._data

    @dataframe.setter
    def dataframe(self, value):
        """Assign a new dataframe

        Parameters
        ----------
        value : pd.DataFrame
        """
        self.beginResetModel()
        self._source_data = value
        # Copy of the dataframe to handle filtering
        self._data = self._source_data
        self.endResetModel()

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
                if self.isDataFrame:
                    return str(self._data.columns[p_int])
                else:
                    return str(self._data.name)
            if orientation == Qt.Vertical:
                return str(self._data.index[p_int])

        elif role == Qt.DecorationRole and self.columnDecorator and orientation == Qt.Horizontal:
            try:
                dtype = str(self._data[self._data.columns[p_int]].dtype)
                dtype = re.search('(' + '|'.join(TYPE_OPTIONS) + ')', dtype)
                if dtype:
                    dtype = dtype.group()
                else:
                    dtype = 'str'
                return self._type_icons[dtype]
            except Exception as e:
                dumpException(e)
            return None

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
