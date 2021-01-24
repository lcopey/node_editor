from PyQt5.QtWidgets import QTableView, QInputDialog, QLineEdit
from PyQt5.QtCore import Qt
import pandas as pd
from node_editor.utils import dumpException
from .dataframe_model import DataframeModel
from .item_delegate import EditDelegate


class DataframeView(QTableView):
    """Class representing a view of a :class:`~DataFrameModel`"""

    def __init__(self, parent=None, dataframe: pd.DataFrame = None, editable=False):
        super(DataframeView, self).__init__(parent)
        # header = MyHeader()
        # self.setHorizontalHeader(QHeaderView(Qt.Horizontal))
        self.horizontalHeader().setSectionsMovable(True)
        self.verticalHeader().setSectionsMovable(True)
        # Add sort support
        self.horizontalHeader().setSortIndicatorShown(True)
        self.setSortingEnabled(True)
        # strech last header
        # self.horizontalHeader().setStretchLastSection(True)
        self.editable = editable

        if self.editable:
            # Edit delegate to control the inputs in the cell
            self.setItemDelegate(EditDelegate())
            # On header double click, trigger changeHeader
            self.horizontalHeader().sectionDoubleClicked.connect(self.changeHorizontalHeader)

        if dataframe is not None:
            self.setDataFrame(dataframe, editable=self.editable)

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
