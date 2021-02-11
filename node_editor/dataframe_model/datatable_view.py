from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pandas as pd
import numpy as np
from dataclasses import dataclass, field, asdict
from node_editor.utils import dumpException

from typing import Dict, List, Union, Iterable, Any


class DataTableView(QTableView):
    def __init__(self, parent=None, dataframe: Union[pd.DataFrame, pd.Series] = None):
        super().__init__(parent)
        model = DataTableModel(self, dataframe)
        # deactivate header
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))

        # deactivate scrollbar, they are handled by their respective headerview in the dataframe_viewer
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # assign model
        self.setModel(model)

    def setDataFrame(self, dataframe: Union[pd.DataFrame, pd.Series]):
        self.model().setDataSource(dataframe)

    @property
    def dataframe(self):
        return self.model().dataframe


@dataclass
class Filter:
    expr: str
    enabled: bool
    failed: bool


def _align(value: Any) -> Qt.AlignmentFlag:
    """Align values in the `DataTableModel` cell according to their type

    Parameters
    ----------
    value: Any
        value to align

    Returns
    -------
    Qt.AlignmentFlag
        Qt.AlignVCenter + Qt.AlignRight in case of numeric type else
         Qt.AlignVCenter + Qt.AlignLeft
    """
    if pd.api.types.is_numeric_dtype(value):
        return Qt.AlignVCenter + Qt.AlignRight
    else:
        return Qt.AlignVCenter + Qt.AlignLeft


class DataTableModel(QAbstractTableModel):
    def __init__(self, parent=None, dataframe: Union[pd.DataFrame, pd.Series] = None):
        """Model handling values taken either from a DataFrame or a Series

        Parameters
        ----------
        parent

        Instance attributes
        -------------------
        _source_dataframe : pd.DataFrame
            Data source
        _dataframe : pd.DataFrame
            Data sorted or filtered
        filters : List[Filter]
            list of `Filter` to apply
        """
        try:
            super().__init__(parent=parent)
            # init attributes
            self._source_dataframe: Union[pd.DataFrame, pd.Series, None] = None
            self._dataframe: Union[pd.DataFrame, pd.Series, None] = None
            self.dataframe = dataframe
        except Exception as e:
            dumpException(e)

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, value):
        self.beginResetModel()
        if value is None:
            value = pd.DataFrame()  # Default value for DataFrame
        if isinstance(value, pd.Series):
            value = value.to_frame()  # in case of Series cast to DataFrame
        self._source_dataframe = self._dataframe = value
        self.endResetModel()

    def setDataSource(self, dataframe: Union[pd.Series, pd.DataFrame]):
        """Helper function for setting a new dataframe in the model

        Parameters
        ----------
        dataframe: Union[pd.Series, pd.DataFrame]
        """
        self.dataframe = dataframe

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        """Access to data"""
        if index.isValid():
            value = self._dataframe.iloc[index.row(), index.column()]
            if role == Qt.DisplayRole or role == Qt.ToolTipRole:
                if pd.isna(value):
                    return ''

                # Float formatting
                if isinstance(value, (float, np.floating)):
                    if not role == Qt.ToolTipRole:
                        return "{:.4f}".format(value)

                return str(value)
            elif role == Qt.TextAlignmentRole:
                return _align(value)
        return None

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self._dataframe.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return self._dataframe.shape[1]

    def flags(self, index: QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        """Set value of dataframe"""
        pass

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        """to implement ? not sure"""
        pass

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        """Handle sorting of inner value of dataframe"""
        pass

    def addFilter(self, filter: Filter):
        """Add `Filter` to list of filters"""
        pass

    def applyFilters(self):
        """Apply filters, update value in dataframe"""
        pass

    def editFilter(self, index):
        pass

    def toggleFilter(self, index):
        pass
