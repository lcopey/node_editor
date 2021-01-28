from PyQt5.QtWidgets import QTableView, QInputDialog, QLineEdit, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
import pandas as pd
from node_editor.utils import dumpException
from .dataframe_model import DataframeModel
from .item_delegate import EditDelegate
from .filter_header import FilterHeader


class DataframeView(QTableView):
    """Class representing a view of a :class:`~DataFrameModel`"""

    def __init__(self, parent=None, dataframe: pd.DataFrame = None, editable=False, filterable=False):
        super(DataframeView, self).__init__(parent)
        self.filterable = filterable
        self.editable = editable

        if self.filterable:
            # Define filter header as horizontal header
            self.header = FilterHeader(self)
            self.setHorizontalHeader(self.header)
            self.header.setSectionsMovable(True)
            # Add sort support
            self.header.setSortIndicatorShown(True)
            self.setSortingEnabled(True)
            self.header.setSectionsClickable(True)
            # add support for filter
            self.header.filterActivated.connect(self.filterDataFrame)
            # strech last header
            # self.horizontalHeader().setStretchLastSection(True)

        # Vertical header
        self.verticalHeader().setSectionsMovable(True)

        if self.editable:
            # Edit delegate to control the inputs in the cell
            self.setItemDelegate(EditDelegate())
            # On header double click, trigger changeHeader
            self.horizontalHeader().sectionDoubleClicked.connect(self.changeHorizontalHeader)

        if dataframe is not None:
            self.setDataFrame(dataframe, editable=self.editable)

    def getParams(self):
        params = {'parent': self.parent(),
                  'dataframe': self.getDataFrame(),
                  'editable': self.editable,
                  'filterable': self.filterable}
        return params

    def copy(self):
        """Returns a new instance of current dataview"""
        return DataframeView(**self.getParams())

    def changeHorizontalHeader(self, index):
        try:
            oldHeader = self.model().headerData(index, Qt.Horizontal, Qt.DisplayRole)
            value, valid = QInputDialog.getText(self,
                                                'Change header label for column %d' % index,
                                                'Header:',
                                                QLineEdit.Normal,
                                                str(oldHeader))
            if valid:
                self.model().setHeaderValue(index, Qt.Horizontal, value)
        except Exception as e:
            dumpException(e)

    def setDataFrame(self, dataframe: pd.DataFrame, editable=False):
        """Define the dataframe through a new `DataframeModel`

        Parameters
        ----------
        dataframe : pd.DataFrame
            dataframe holding the data
        editable : bool
            flag setting the `DataframeModel` as editable
        """
        dataframe_model = DataframeModel(view=self, dataframe=dataframe, editable=editable)
        self.header.setFilterBoxes(dataframe_model.columnCount())
        # Connect filter from model to event in FilterHeader
        super().setModel(dataframe_model)

    def getDataFrame(self):
        """Returns dataframe currently hold in the `DataframeModel`

        Returns
        -------
        pd.DataFrame
            dataframe currently hold in the `DataframeModel`
        """
        return self.model().dataframe

    def filterDataFrame(self):
        self.model().filter()
