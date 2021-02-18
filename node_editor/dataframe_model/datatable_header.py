from PyQt5.QtWidgets import QTableView, QSizePolicy, QAbstractItemView, QApplication
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, QItemSelectionModel, QItemSelection, QObject, \
    QEvent, QPoint
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np

from typing import Dict, List, Union, Iterable, Any, TYPE_CHECKING
from node_editor.utils import dumpException

if TYPE_CHECKING:
    from .dataframe_viewer import DataFrameView

DEBUG = True


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

    def isHorizontal(self):
        return self.orientation == Qt.Horizontal

    def isVertical(self):
        return self.orientation == Qt.Vertical

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
        if self.isHorizontal():
            return self.dataframe.columns.nlevels
        elif self.isVertical():
            return self.dataframe.index.shape[0]

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            value = None
            if self.isHorizontal():
                # Header corresponds to columns
                if isinstance(self.dataframe.columns, pd.MultiIndex):
                    value = self.dataframe.columns[col][row]
                else:
                    value = self.dataframe.columns[col]
            elif self.isVertical():
                if isinstance(self.dataframe.index, pd.MultiIndex):
                    value = self.dataframe.index[row][col]
                else:
                    value = self.dataframe.index[row]
            if pd.isna(value):
                return ''
            else:
                return str(value)

    # def updateModel(self):
    #     """Update model - Is typically called when new dataframe is set upon the DataFrameView"""
    #     self.layoutAboutToBeChanged.emit()
    #     # self.beginResetModel()
    #     self._dataframe = self.dataframeView.dataframe
    #     # self.endResetModel()
    #     self.layoutChanged.emit()


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
        self.dataView = parent.dataView  # reference to table
        self.orientation = orientation

        # variables for resize event
        self._header_being_resized = None
        self._resize_start_position = None
        self._header_initial_size = None

        # define model data
        model = HeaderModel(dataframeView=parent, parent=self)
        self.setModel(model)

        # install eventFilter
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)

        # setup ui
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        # Set stretch parameters of headers
        if self.isHorizontal():
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        else:
            self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

        font = QFont()
        font.setBold(True)
        self.setFont(font)

        self.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        # Set initial size
        self.set_spans()
        self.init_column_sizes()
        self.resize(self.sizeHint())

    def isHorizontal(self):
        return self.orientation == Qt.Horizontal

    def isVertical(self):
        return self.orientation == Qt.Vertical

    def sizeHint(self):
        # Columm headers
        if self.isHorizontal():
            # Width of DataTableView
            width = self.dataView.sizeHint().width() + self.verticalHeader().width()
            # Height
            height = 2 * self.frameWidth()  # Account for border & padding
            for i in range(self.model().rowCount()):
                height += self.rowHeight(i)

        # Index header
        else:
            # Height of DataTableView
            height = self.dataView.sizeHint().height() + self.horizontalHeader().height()
            # Width
            width = 2 * self.frameWidth()  # Account for border & padding
            for i in range(self.model().columnCount()):
                width += self.columnWidth(i)
        return QSize(width, height)

    # This is needed because otherwise when the horizontal header is a single row it will add whitespace to be bigger
    def minimumSizeHint(self):
        if self.isHorizontal():
            return QSize(0, self.sizeHint().height())
        else:
            return QSize(self.sizeHint().width(), 0)

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

            if self.isHorizontal():
                # Removes the higher levels so that only the lowest level of the header affects the data table selection
                last_row_ix = self.dataframe.columns.nlevels - 1
                last_col_ix = self.model().columnCount() - 1
                higher_levels = QItemSelection(
                    self.model().index(0, 0),
                    self.model().index(last_row_ix - 1, last_col_ix),
                )
                selection.merge(higher_levels, QItemSelectionModel.Deselect)

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
            if self.isVertical():
                # Removes the higher levels so that only the lowest level of the header affects the data table selection
                last_row_ix = self.model().rowCount() - 1
                last_col_ix = self.dataframe.index.nlevels - 1
                higher_levels = QItemSelection(
                    self.model().index(0, 0),
                    self.model().index(last_row_ix, last_col_ix - 1),
                )
                selection.merge(higher_levels, QItemSelectionModel.Deselect)

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

    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        try:
            # start dragging process
            if event.type() == QEvent.MouseButtonPress:
                # store mouse position and header being resized
                mousePosition = event.pos()
                self._header_being_resized = self.overHeaderEdge(mousePosition)
                if self._header_being_resized is not None:
                    self.print('>>Resize triggered')
                    self.print('Header selected : ', self._header_being_resized)
                    # store initial header size
                    if self.isHorizontal():
                        self._resize_start_position = mousePosition.x()
                        self._header_initial_size = self.columnWidth(self._header_being_resized)
                    else:
                        self._resize_start_position = mousePosition.y()
                        self._header_initial_size = self.rowHeight(self._header_being_resized)
                    return True
            # end dragging process
            elif event.type() == QEvent.MouseButtonRelease:
                self._header_being_resized = None
                return True

            # Handle active drag resizing
            elif event.type() == QEvent.MouseMove:
                if self._header_being_resized is not None:
                    self.print('>>Resizing')
                    mousePosition = event.pos()
                    if self.isHorizontal():
                        new_size = self._header_initial_size + mousePosition.x() - self._resize_start_position
                        self.setColumnWidth(self._header_being_resized, new_size)
                        self.dataView.setColumnWidth(self._header_being_resized, new_size)
                    else:
                        new_size = self._header_initial_size + mousePosition.y() - self._resize_start_position
                        self.setRowHeight(self._header_being_resized, new_size)
                        self.dataView.setRowHeight(self._header_being_resized, new_size)
                    return True
                else:
                    # Change cursor upon hover
                    if self.overHeaderEdge(event.pos()) is not None:
                        if self.isHorizontal():
                            # QApplication.setOverrideCursor(Qt.SplitHCursor)
                            self.setCursor(Qt.SplitHCursor)
                        else:
                            # QApplication.setOverrideCursor(Qt.SplitVCursor)
                            self.setCursor(Qt.SplitVCursor)
                    else:
                        # QApplication.restoreOverrideCursor()
                        self.setCursor(Qt.ArrowCursor)

        except Exception as e:
            dumpException(e)
        return False

    def overHeaderEdge(self, pos: QPoint, margin: int = 3):
        """Helper function - returns the index of the column this x position is on the right edge of"""
        # Return the index of the column this x position is on the right edge of
        if self.isHorizontal():
            x = pos.x()
            if self.columnAt(x - margin) != self.columnAt(x + margin):
                if self.columnAt(x + margin) == 0:
                    # We're at the left edge of the first column
                    return None
                else:
                    return self.columnAt(x - margin)
            else:
                return None

        # Return the index of the row this y position is on the top edge of
        elif self.isVertical():
            y = pos.y()
            if self.rowAt(y - margin) != self.rowAt(y + margin):
                if self.rowAt(y + margin) == 0:
                    # We're at the top edge of the first row
                    return None
                else:
                    return self.rowAt(y - margin)
            else:
                return None

    # def updateModel(self):
    #     """Update model - Is typically called when new dataframe is set upon the DataFrameView"""
    #     model: HeaderModel = self.model()
    #     model.updateModel()
    #     self.set_spans()
    #     self.init_column_sizes()
    #     self.resize(self.sizeHint())

    # Fits columns to contents but with a minimum width and added padding
    def init_column_sizes(self):
        padding = 5

        # Columns match columns of content with header
        if self.isHorizontal():
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
                self.dataView.setColumnWidth(col, new_width)

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
            if self.isHorizontal():
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
                if self.isHorizontal():
                    self.setSpan(nlevel, spans[n] + 1, 1, span_size)
                else:
                    self.setSpan(spans[n] + 1, nlevel, span_size, 1)

    def print(self, *args):
        if self.isHorizontal():
            print('> ColumnHeader ', *args)
        else:
            print('> IndexHeader ', *args)
