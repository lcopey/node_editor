from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal
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
        self._columnsListWidget = QListWidget()
        self._indexListWidget = QListWidget()
        self._valuesListWidget = QListWidget()

        # layout for selecting the column name
        selectLayout = QHBoxLayout()
        selectLayout.addWidget(self._selectListWidget)
        bttnLayout = QVBoxLayout()
        self._add_to_col = QPushButton()
        self._add_to_col.setText('To columns')
        self._add_to_col.clicked.connect(self._move_items_to_col)
        self._add_to_idx = QPushButton()
        self._add_to_idx.setText('To index')
        self._add_to_idx.clicked.connect(self._move_items_to_idx)
        self._add_to_val = QPushButton()
        self._add_to_val.setText('To values')
        self._add_to_val.clicked.connect(self._move_items_to_val)
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
        self._col_del.clicked.connect(self._remove_items_from_col)
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
        self._idx_del.clicked.connect(self._remove_items_from_idx)
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
        self._val_del.clicked.connect(self._remove_items_from_val)
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

    def _move_items_to(self, fromList: QListWidget, destList: QListWidget):
        item = fromList.takeItem(fromList.currentRow())
        destList.addItem(item)
        self.forcedEval()

    def _move_items_to_col(self):
        self._move_items_to(self._selectListWidget, self._columnsListWidget)

    def _move_items_to_idx(self):
        self._move_items_to(self._selectListWidget, self._indexListWidget)

    def _move_items_to_val(self):
        self._move_items_to(self._selectListWidget, self._valuesListWidget)

    def _remove_items_from_col(self):
        self._move_items_to(self._columnsListWidget, self._selectListWidget)

    def _remove_items_from_idx(self):
        self._move_items_to(self._indexListWidget, self._selectListWidget)

    def _remove_items_from_val(self):
        self._move_items_to(self._valuesListWidget, self._selectListWidget)

    def _get_pivot_args(self):
        kwargs = {}
        kwargs['index'] = [self._indexListWidget.item(n).text() for n in range(self._indexListWidget.count())]
        kwargs['columns'] = [self._columnsListWidget.item(n).text() for n in range(self._columnsListWidget.count())]
        kwargs['values'] = [self._valuesListWidget.item(n).text() for n in range(self._valuesListWidget.count())]
        for key in ['index', 'columns', 'values']:
            if len(kwargs[key]) == 0:
                kwargs[key] = None
        return kwargs

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

        evaluate = self._columnsListWidget.count() > 1
        evaluate &= self._indexListWidget.count() > 1
        evaluate &= self._valuesListWidget > 1
        if evaluate:
            kwargs = self._get_pivot_args()
            self.value = self.input_val.pivot_table(**kwargs)

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
