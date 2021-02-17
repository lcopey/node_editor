from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QObject, QEvent
from .datatable_view import DataTableView
from .datatable_header import HeaderView
import pandas as pd

from typing import Dict, List, Union, Iterable, Any


class DataFrameView(QWidget):
    def __init__(self, parent=None, dataframe: Union[pd.DataFrame, pd.Series] = None):
        super().__init__(parent=parent)
        self.dataView = DataTableView(parent=self, dataframe=dataframe)
        # Create headers
        self.columnHeader = HeaderView(parent=self, orientation=Qt.Horizontal)
        self.indexHeader = HeaderView(parent=self, orientation=Qt.Vertical)

        # TODO minsize larger than node ?
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Linking scrollbars
        # Scrolling in data table also scrolls the headers
        self.dataView.horizontalScrollBar().valueChanged.connect(self.columnHeader.horizontalScrollBar().setValue)
        self.dataView.verticalScrollBar().valueChanged.connect(self.indexHeader.verticalScrollBar().setValue)

        # Scrolling in headers also scrolls the data table
        self.columnHeader.horizontalScrollBar().valueChanged.connect(self.dataView.horizontalScrollBar().setValue)
        self.indexHeader.verticalScrollBar().valueChanged.connect(self.dataView.verticalScrollBar().setValue)
        # deactivate the other scroll bar
        self.columnHeader.verticalScrollBar().valueChanged.connect(lambda: None)
        self.indexHeader.horizontalScrollBar().valueChanged.connect(lambda: None)

        # Set up layout
        self.gridLayout = QGridLayout()

        # Add items to grid layout
        # self.corner_widget = QWidget()
        # self.corner_widget.setAttribute(Qt.WA_StyledBackground)
        # self.corner_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # alignment = Qt.AlignLeft | Qt.AlignTop
        # self.gridLayout.addWidget(self.corner_widget, 0, 0)
        self.gridLayout.addWidget(self.columnHeader, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.indexHeader, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.dataView, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.dataView.horizontalScrollBar(), 2, 1, 1, 1)
        self.gridLayout.addWidget(self.dataView.verticalScrollBar(), 1, 2, 1, 1)
        # self.gridLayout.setColumnStretch(0, 0)
        # self.gridLayout.setRowStretch(0, 0)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setRowStretch(1, 1)
        # self.gridLayout.setColumnStretch(2, 0)
        self.gridLayout.setRowStretch(2, 0)

        # set margin of content and layout
        self.indexHeader.setContentsMargins(0, 0, 0, 0)
        self.columnHeader.setContentsMargins(0, 0, 0, 0)
        self.dataView.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(2)
        self.setLayout(self.gridLayout)

    # def setDataFrame(self, dataframe: Union[pd.DataFrame, pd.Series]):
    #     self.dataView.setDataFrame(dataframe)
    #     self.indexHeader.updateModel()
    #     self.columnHeader.updateModel()
    #     # TODO Trying to debug...
    #     # self.corner_widget.setFixedWidth(self.indexHeader.width())
    #     # self.corner_widget.setFixedHeight(self.columnHeader.height())

    @property
    def dataframe(self):
        return self.dataView.model().dataframe
