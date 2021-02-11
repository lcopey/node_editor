from PyQt5.QtWidgets import QItemDelegate, QComboBox, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon
import pandas as pd
from node_editor.dataframe_model_bak import DataframeModel

from node_editor.utils import dumpException
from typing import Any

TYPE_OPTIONS = ['str', 'int', 'float', 'bool']


class TypeChooserModel(DataframeModel):
    def __init__(self, view: 'QTableView' = None):
        super().__init__(view=view, dataframe=pd.Series(name='Type'), editable=True, columnDecorator=False)
        self._type_icons = {key: QIcon('./icons/{}_icon.svg'.format(key)) for key in TYPE_OPTIONS}

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.DecorationRole:
            return self._type_icons[self._data.iloc[index.row()]]
        else:
            return super().data(index, role)


# class TypeChooserModel(QAbstractTableModel):
#     def __init__(self, ):
#         super().__init__()
#         self._data = None
#         self._type_icons = {key: QIcon('./icons/{}_icon.svg'.format(key)) for key in TYPE_OPTIONS}
#
#     def flags(self, index):
#         flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
#         return flags
#
#     def rowCount(self, parent=None):
#         if self._data is not None:
#             return self._data.shape[0]
#         return 0
#
#     def columnCount(self, parent=None):
#         return 1
#
#     def data(self, index, role=Qt.DisplayRole):
#         try:
#             if index.isValid():
#                 if role == Qt.DisplayRole:
#                     return self._data.iloc[index.row()]
#                 # elif role == Qt.TextAlignmentRole:
#                 #     return _align(value)
#                 elif role == Qt.DecorationRole:
#                     return self._type_icons[self._data.iloc[index.row()]]
#
#         except Exception as e:
#             dumpException(e)
#
#         return None
#
#     def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
#         try:
#             if role == Qt.EditRole:
#                 self._data.iloc[index.row()] = value
#                 return True
#         except Exception as e:
#             dumpException(e)
#
#     def getData(self):
#         return self._data
#
#     def setDataSource(self, data: pd.Series):
#         self.beginResetModel()
#         self._data = data
#         self.endResetModel()
#
#     def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
#         if role == Qt.DisplayRole:
#             if orientation == Qt.Vertical:
#                 return self._data.index[section]
#             else:
#                 return 'Type'
#
#         return None


class ErrorTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._data = None

    def getData(self):
        return self._data

    def setDataSource(self, data: pd.DataFrame):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def rowCount(self, parent=None):
        if self._data is not None:
            return self._data.shape[0]
        return 0

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        try:
            if index.isValid():
                if role == Qt.DisplayRole:
                    return self._data.iloc[index.row(), index.column()]
                # elif role == Qt.TextAlignmentRole:
                #     return _align(value)

        except Exception as e:
            dumpException(e)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return self._data.index[section]
            else:
                return ['Old', 'New']

        return None


class ComboDelegate(QItemDelegate):
    def __init__(self, parent=None, options=None):
        super().__init__(parent=parent)
        if not options:
            options = []
        self.options = options

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.options)
        editor.currentIndexChanged.connect(self.currentItemChanged)

        return editor

    def setEditorData(self, editor, index):
        try:
            value = index.data(Qt.DisplayRole)
            num = self.options.index(value)
            editor.setCurrentIndex(num)
        except Exception as e:
            dumpException(e)

    @pyqtSlot()
    def currentItemChanged(self):
        try:
            print(self.sender())
            self.commitData.emit(self.sender())
        except Exception as e:
            dumpException(e)
