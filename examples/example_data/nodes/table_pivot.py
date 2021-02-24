from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QFontMetrics
from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory
import pandas as pd
from typing import Union


@NodeFactory.register()
class OpNode_PivotTable(DataNode):
    icon = 'icons/table-pivot-64.svg'
    op_title = 'Pivot'
    content_label = ''
    content_label_objname = 'data_node_pivot_table'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.columns: Union[pd.Index, None] = None

    def initPropertiesWidget(self):
        self.propertiesWidget = QWidget()
        self.propertiesWidget.setMinimumWidth(100)

        # global layout
        outerLayout = QVBoxLayout()
        self._selectListWidget = QListWidget()
        self._selectListWidget.setViewMode(QListWidget.IconMode)
        self._selectListWidget.setResizeMode(QListView.Adjust)
        self._selectListWidget.setSpacing(5)
        # font = QFont('Ubuntu', 8)
        # self._selectListWidget.setFont(font)
        # self._selectListWidget.setGridSize(QSize(64, QFontMetrics(font).height() + 10))

        self._columnsListWidget = QListWidget()
        self._indexListWidget = QListWidget()
        self._valuesListWidget = QListWidget()

        # layout for selecting the column name
        selectLayout = QHBoxLayout()
        selectLayout.addWidget(self._selectListWidget)
        bttnLayout = QVBoxLayout()
        self._add_to_col = QPushButton()
        self._add_to_col.setText('To columns')
        self._add_to_col.clicked.connect(self._moveItemsToCol)
        self._add_to_idx = QPushButton()
        self._add_to_idx.setText('To index')
        self._add_to_idx.clicked.connect(self._moveItemsToIdx)
        self._add_to_val = QPushButton()
        self._add_to_val.setText('To values')
        self._add_to_val.clicked.connect(self._moveItemsToVal)
        bttnLayout.addWidget(self._add_to_col)
        bttnLayout.addWidget(self._add_to_idx)
        bttnLayout.addWidget(self._add_to_val)
        selectLayout.addLayout(bttnLayout)

        # layout holding the columns values
        columnLayout = QHBoxLayout()
        columnLayout.addWidget(self._columnsListWidget)
        bttnLayout = QVBoxLayout()
        self._col_up = QPushButton()
        self._col_down = QPushButton()
        self._col_del = QPushButton()
        self._col_del.clicked.connect(self._removeItemsFromCol)
        bttnLayout.addWidget(self._col_up)
        bttnLayout.addWidget(self._col_down)
        bttnLayout.addWidget(self._col_del)
        columnLayout.addLayout(bttnLayout)

        # layout holding the index values
        indexLayout = QHBoxLayout()
        indexLayout.addWidget(self._indexListWidget)
        bttnLayout = QVBoxLayout()
        self._idx_up = QPushButton()
        self._idx_down = QPushButton()
        self._idx_del = QPushButton()
        self._idx_del.clicked.connect(self._removeItemsFromIdx)
        bttnLayout.addWidget(self._idx_up)
        bttnLayout.addWidget(self._idx_down)
        bttnLayout.addWidget(self._idx_del)
        indexLayout.addLayout(bttnLayout)

        # layout holding the values
        valuesLayout = QHBoxLayout()
        valuesLayout.addWidget(self._valuesListWidget)
        bttnLayout = QVBoxLayout()
        self._val_up = QPushButton()
        self._val_down = QPushButton()
        self._val_del = QPushButton()
        self._val_del.clicked.connect(self._removeItemsFromVal)
        bttnLayout.addWidget(self._val_up)
        bttnLayout.addWidget(self._val_down)
        bttnLayout.addWidget(self._val_del)
        valuesLayout.addLayout(bttnLayout)

        # add all the elements to the global layout
        outerLayout.addLayout(selectLayout)
        outerLayout.addLayout(columnLayout)
        outerLayout.addLayout(indexLayout)
        outerLayout.addLayout(valuesLayout)

        self.propertiesWidget.setLayout(outerLayout)

    def updatePropertiesWidget(self):
        self._selectListWidget.clear()
        if self.columns is not None:
            for column in self.columns:
                # add item to listWidget
                item = QListWidgetItem()
                item.setText(str(column))
                self._selectListWidget.addItem(item)

    def _moveItemsTo(self, fromList: QListWidget, destList: QListWidget):
        item = fromList.takeItem(fromList.currentRow())
        destList.addItem(item)
        self.forcedEval()

    def _moveItemsToCol(self):
        self._moveItemsTo(self._selectListWidget, self._columnsListWidget)

    def _moveItemsToIdx(self):
        self._moveItemsTo(self._selectListWidget, self._indexListWidget)

    def _moveItemsToVal(self):
        self._moveItemsTo(self._selectListWidget, self._valuesListWidget)

    def _removeItemsFromCol(self):
        self._moveItemsTo(self._columnsListWidget, self._selectListWidget)

    def _removeItemsFromIdx(self):
        self._moveItemsTo(self._indexListWidget, self._selectListWidget)

    def _removeItemsFromVal(self):
        self._moveItemsTo(self._valuesListWidget, self._selectListWidget)

    def getNodeSettings(self):
        kwargs = {}
        kwargs['index'] = [self._indexListWidget.item(n).text() for n in range(self._indexListWidget.count())]
        kwargs['columns'] = [self._columnsListWidget.item(n).text() for n in range(self._columnsListWidget.count())]
        kwargs['values'] = [self._valuesListWidget.item(n).text() for n in range(self._valuesListWidget.count())]
        for key in ['index', 'columns', 'values']:
            if len(kwargs[key]) == 0:
                kwargs[key] = None
        return kwargs

    def restoreNodeSettings(self, data: dict) -> bool:
        kwargs = data['node_settings']
        for value, wdg in zip(('index', 'columns', 'values'),
                              (self._indexListWidget, self._columnsListWidget, self._valuesListWidget)):
            if kwargs[value]:
                new_item = QListWidgetItem()
                new_item.setText(str(value))
                wdg.addItem(new_item)

        return True

    def evalImplementation(self, force=False):
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
            new_columns = self.input_val.columns
        else:
            self.columns = None
            new_columns = None

        # TODO support multiindex
        if isinstance(new_columns, pd.MultiIndex):
            self.setToolTip('Multilevel index is not yet supported')
            self.markInvalid()
            return

        # Compare if new columns are the same as the old one
        if self.columns is None or not (self.columns.equals(new_columns)):
            # Update the properties toolbar accordingly
            self.columns = new_columns
            self.updatePropertiesWidget()

        if self.columns is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        evaluate = self._columnsListWidget.count() >= 1
        evaluate &= self._indexListWidget.count() >= 1
        evaluate &= self._valuesListWidget.count() >= 1
        if evaluate:
            kwargs = self.getNodeSettings()
            self.value = self.input_val.pivot_table(**kwargs)

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
