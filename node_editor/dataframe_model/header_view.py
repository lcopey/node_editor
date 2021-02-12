from PyQt5.QtWidgets import QTableView, QSizePolicy, QAbstractItemView
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, QItemSelectionModel, QItemSelection
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np

from typing import Dict, List, Union, Iterable, Any, TYPE_CHECKING
from node_editor.utils import dumpException

if TYPE_CHECKING:
    from .dataframe_viewer import DataFrameView


class HeaderModel(QAbstractTableModel):
    """Model handling values taken either from a DataFrame or a Series index or columns"""

    def __init__(self, parent: 'HeaderView', dataframeView: 'DataFrameView'):
        """Model handling values from parent DataFrameView

        Parameters
        ----------
        parent: DataFrameView
            DataFrameView handling the corresponding headerView
        orientation: Qt.Orientation
            if Qt.Horizontal, the HeaderModel will contain column information
            if Qt.Vertical, the HeaderModel will contain index information
        """
        super().__init__(parent)
        self.dataframeView = dataframeView
        self.orientation = parent.orientation
        self._dataframe = parent.dataframe

    @property
    def dataframe(self):
        return self._dataframe

    def updateModel(self):
        """Update model - Is typically called when new dataframe is set upon the DataFrameView"""
        self.beginResetModel()
        self._dataframe = self.dataframeView.dataframe
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """Columns count is either the count of columns in case orientation is Horizontal.
        Else it corresponds to the count of levels of the index"""
        if self.orientation == Qt.Horizontal:
            return self.dataframe.columns.shape[0]
        else:
            return self.dataframe.index.nlevels

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """Rows count is either the count of rows in case orientation is Vertical.
        Else it corresponds to the count of levels of the columns"""
        if self.orientation == Qt.Horizontal:
            return self.dataframe.columns.nlevels
        elif self.orientation == Qt.Vertical:
            return self.dataframe.index.shape[0]

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            if self.orientation == Qt.Horizontal:
                # Header corresponds to columns
                if isinstance(self.dataframe.columns, pd.MultiIndex):
                    return str(self.dataframe.columns[col][row])
                else:
                    return str(self.dataframe.columns[col])
            elif self.orientation == Qt.Vertical:

                if isinstance(self.dataframe.index, pd.MultiIndex):
                    return str(self.dataframe.index[row][col])
                else:
                    return str(self.dataframe.index[row])


class HeaderView(QTableView):
    """View displaying datas from a HeaderModel"""

    def __init__(self, parent: 'DataFrameView', orientation: Qt.Orientation):
        """View displaying values from parent DataFrameView

        Parameters
        ----------
        parent: DataFrameView
            DataFrameView handling the corresponding headerView
        orientation: Qt.Orientation
            if Qt.Horizontal, the HeaderModel will contain column information
            if Qt.Vertical, the HeaderModel will contain index information
        """
        super().__init__(parent)
        self.dataframe: pd.DataFrame = parent.dataframe
        self.table = parent.dataView  # reference to table
        self.orientation = orientation
        # define model data
        model = HeaderModel(dataframeView=parent, parent=self)
        self.setModel(model)

        # setup ui
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        # Set stretch parameters of headers
        if self.orientation == Qt.Horizontal:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        else:
            self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

        font = QFont()
        font.setBold(True)
        self.setFont(font)

        self.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        self.set_spans()
        self.init_column_sizes()

        # Set initial size
        self.resize(self.sizeHint())

    def updateModel(self):
        """Update model - Is typically called when new dataframe is set upon the DataFrameView"""
        self.model().updateModel()

    def sizeHint(self):
        # Columm headers
        if self.orientation == Qt.Horizontal:
            # Width of DataTableView
            width = self.table.sizeHint().width() + self.verticalHeader().width()
            # Height
            height = 2 * self.frameWidth()  # Account for border & padding
            for i in range(self.model().rowCount()):
                height += self.rowHeight(i)

        # Index header
        else:
            # Height of DataTableView
            height = self.table.sizeHint().height() + self.horizontalHeader().height()
            # Width
            width = 2 * self.frameWidth()  # Account for border & padding
            for i in range(self.model().columnCount()):
                width += self.columnWidth(i)
        return QSize(width, height)

    # This is needed because otherwise when the horizontal header is a single row it will add whitespace to be bigger
    def minimumSizeHint(self):
        if self.orientation == Qt.Horizontal:
            return QSize(0, self.sizeHint().height())
        else:
            return QSize(self.sizeHint().width(), 0)

    # Fits columns to contents but with a minimum width and added padding
    def init_column_sizes(self):
        padding = 5

        # Columns match columns of content with header
        if self.orientation == Qt.Horizontal:
            min_size = 0

            self.resizeColumnsToContents()
            for col in range(self.model().columnCount()):
                width = self.columnWidth(col)
                if width + padding < min_size:
                    new_width = min_size
                else:
                    new_width = width + padding
                # Match column width of content with header
                self.setColumnWidth(col, new_width)
                self.table.setColumnWidth(col, new_width)

        else:
            # Index, only set the width
            self.resizeColumnsToContents()
            for col in range(self.model().columnCount()):
                width = self.columnWidth(col)
                self.setColumnWidth(col, width + padding)

    def set_spans(self):
        """Adjust spans of the table to display multiheader like"""
        self.clearSpans()
        try:
            # Find spans for horizontal HeaderView
            if self.orientation == Qt.Horizontal:
                self._adjust_spans(self.dataframe.columns)
            else:
                self._adjust_spans(self.dataframe.index)

        except Exception as e:
            dumpException(e)

    def _adjust_spans(self, index: Union[pd.Index, pd.MultiIndex]):
        """Compute spans"""
        if isinstance(index, pd.MultiIndex):
            levels = np.stack([np.array(value) for value in index]).T
        else:
            levels = np.array([index])

        for nlevel, level in enumerate(levels):
            # detect where level are discontinuous
            spans = list(np.where(level[1:] != level[:-1])[0])
            # add the first and last cell if necessary
            if 0 not in spans:
                spans.insert(0, -1)
            if len(level) - 1 not in spans:
                spans.append(len(level) - 1)
            # only check if span if larger thant one cell
            for n in np.where(np.diff(list(spans)) > 1)[0]:
                span_size = spans[n + 1] - (spans[n] + 1) + 1
                if self.orientation == Qt.Horizontal:
                    self.setSpan(nlevel, spans[n] + 1, 1, span_size)
                else:
                    self.setSpan(spans[n] + 1, nlevel, span_size, 1)

    def onSelectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        """Select corresponding cells

        Parameters
        ----------
        selected: QItemSelection
        deselected: QItemSelection

        Returns
        -------

        """
        if self.hasFocus():
            dataView = self.parent().dataView
            selection = self.selectionModel().selection()

            if self.orientation == Qt.Horizontal:
                # Removes the higher levels so that only the lowest level of the header affects the data table selection
                # last_row_ix = self.dataframe.columns.nlevels - 1
                # last_col_ix = self.model().columnCount() - 1
                # higher_levels = QItemSelection(
                #     self.model().index(0, 0),
                #     self.model().index(last_row_ix - 1, last_col_ix),
                # )
                # selection.merge(higher_levels, QItemSelectionModel.Deselect)
                # Unselect the indexHeader
                indexHeader: HeaderView = self.parent().indexHeader
                indexModel = indexHeader.model()
                indexSelect = QItemSelection(indexModel.index(0, 0),
                                             indexModel.index(indexModel.rowCount() - 1,
                                                              indexModel.columnCount() - 1))

                indexHeader.selectionModel().select(indexSelect, QItemSelectionModel.Deselect)
                # Select the cells in the data view
                dataView.selectionModel().select(
                    selection,
                    QItemSelectionModel.Columns | QItemSelectionModel.ClearAndSelect,
                )
            if self.orientation == Qt.Vertical:
                # Removes the higher levels so that only the lowest level of the header affects the data table selection
                # last_row_ix = self.model().rowCount() - 1
                # last_col_ix = self.dataframe.index.nlevels - 1
                # higher_levels = QItemSelection(
                #     self.model().index(0, 0),
                #     self.model().index(last_row_ix, last_col_ix - 1),
                # )
                # selection.merge(higher_levels, QItemSelectionModel.Deselect)

                # Unselect the columnHeader
                columnHeader: HeaderView = self.parent().columnHeader
                columnModel = columnHeader.model()
                columnSelect = QItemSelection(columnModel.index(0, 0),
                                              columnModel.index(columnModel.rowCount() - 1,
                                                                columnModel.columnCount() - 1))

                columnHeader.selectionModel().select(columnSelect, QItemSelectionModel.Deselect)
                dataView.selectionModel().select(
                    selection,
                    QItemSelectionModel.Rows | QItemSelectionModel.ClearAndSelect,
                )
