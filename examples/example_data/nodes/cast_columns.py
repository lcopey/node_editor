from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout, QComboBox, QItemDelegate
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QIcon
import pandas as pd
import numpy as np

from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory

from typing import List, Any
from node_editor.node_socket import Socket
from node_editor.utils import dumpException

TYPE_OPTIONS = ['str', 'int', 'float', 'bool']
TYPE_MAPPING = {'str': str, 'int': int, 'float': float, 'bool': bool}

def _get_datatype_str(dtype: str):
    for string in TYPE_OPTIONS:
        if string in str(dtype):
            return string
    else:
        return 'str'


class TypeChooserModel(QAbstractTableModel):
    def __init__(self, ):
        super().__init__()
        self._data = None
        self._icons = {key: QIcon('./icons/{}_icon.svg'.format(key)) for key in TYPE_OPTIONS}

    def flags(self, index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return flags

    def rowCount(self, parent=None):
        if self._data is not None:
            return self._data.shape[0]
        return 0

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        try:
            if index.isValid():
                if role == Qt.DisplayRole:
                    return self._data.iloc[index.row()]
                # elif role == Qt.TextAlignmentRole:
                #     return _align(value)
                elif role == Qt.DecorationRole:
                    return self._icons[self._data.iloc[index.row()]]

        except Exception as e:
            dumpException(e)

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        try:
            if role == Qt.EditRole:
                self._data.iloc[index.row()] = value
                return True
        except Exception as e:
            dumpException(e)

    def setDataSource(self, data: pd.Series):
        self._data = data

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return self._data.index[section]
            else:
                return 'Type'

        return None


class ComboDelegate(QItemDelegate):
    def __init__(self, parent=None, options=None):
        super().__init__(parent=parent)
        if not options:
            options = []
        self.options = options

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self.options)
        return combo

    def setEditorData(self, editor, index):
        try:
            value = index.data(Qt.DisplayRole)
            num = self.options.index(value)
            editor.setCurrentIndex(num)
        except Exception as e:
            dumpException(e)


@NodeFactory.register()
class OpNode_CastColumns(DataNode):
    icon = 'icons/table-cast-64.svg'
    op_title = 'Data Type'
    content_label = ''
    content_label_objname = 'data_node_cast_columns'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        self.columnsDtype = None
        super().__init__(scene, inputs=[1, ], outputs=[1])

    def initPropertiesWidget(self):
        self.propertiesWidget = QWidget()

        layout = QVBoxLayout()
        self.columnTypeTable = QTableView()
        delegate = ComboDelegate(self.columnTypeTable, options=TYPE_OPTIONS)
        self.columnTypeTable.setItemDelegate(delegate)
        model = TypeChooserModel()
        self.columnTypeTable.setModel(model)
        layout.addWidget(self.columnTypeTable)

        self.propertiesWidget.setLayout(layout)

    def populateColumnTypeTable(self):
        if self.columnsDtype is not None:
            dtypes = self.columnsDtype.astype(str)
            # extract types from their respective string
            dtypes = dtypes.str.extract('(' + '|'.join(TYPE_OPTIONS) + ')', expand=False)
            dtypes = dtypes.replace(np.nan, 'str')
            model = self.columnTypeTable.model()
            model.beginResetModel()
            model.setDataSource(dtypes)
            model.endResetModel()
            self.columnTypeTable.setColumnWidth(0, 80)

    def updateValue(self):
        self.value = self.input_val.astype(self.columnsDtype)

    def evalImplementation(self):
        self.print('evalImplementation')

        # get first input
        input_node = self.getInput(0)
        if not input_node:
            self.setToolTip('Input is not connected')
            self.markInvalid()
            return

        # get value from input node
        self.input_val = input_node.eval()
        if isinstance(self.input_val, pd.DataFrame):
            new_columns_dtype = self.input_val.dtypes
        else:
            self.columnsDtype = None
            new_columns_dtype = None

        # Compare if new columns are the same as the old one
        if self.columnsDtype is None or not (self.columnsDtype.equals(new_columns_dtype)):
            # Update the properties toolbar accordingly
            self.columnsDtype = new_columns_dtype
            self.populateColumnTypeTable()

        if self.columnsDtype is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        # Store the table with only the selected columns
        self.updateValue()

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
