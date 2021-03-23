from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout, QComboBox, QFrame, QLabel
import pandas as pd
import numpy as np

from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory
from .cast_columns_utils import TYPE_OPTIONS, ComboDelegate, TypeChooserModel

from node_editor.utils import dumpException
from typing import Union


@NodeFactory.register()
class OpNode_CastColumns(DataNode):
    icon = 'resources/table-cast-64.svg'
    op_title = 'Data Type'
    content_label = ''
    content_label_objname = 'data_node_cast_columns'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        self.columnsDtype: Union[pd.Series, None] = None
        super().__init__(scene, inputs=[1, ], outputs=[1])

    def initPropertiesWidget(self):
        self.propertiesWidget = QWidget()
        outerLayout = QVBoxLayout()

        # upperLayout
        upperFrame = QFrame()
        upperFrame.setFrameShape(QFrame.StyledPanel)
        upperFrameLayout = QVBoxLayout()
        # instanciate the corresponding table view
        self.columnTypeTable = QTableView()
        upperFrameLayout.addWidget(self.columnTypeTable)
        upperFrame.setLayout(upperFrameLayout)

        # Add a delegate ComboBox
        delegate = ComboDelegate(self.columnTypeTable, options=TYPE_OPTIONS)
        self.columnTypeTable.setItemDelegate(delegate)
        # on commit data, reevaluate the node
        delegate.commitData.connect(self.updateValue)
        # add the data model
        model = TypeChooserModel()
        self.columnTypeTable.setModel(model)
        # lowerLayout
        lowerFrame = QFrame()
        self.errorTable = QTableView()
        # self.dtypesCombo = QComboBox()
        frameTitle = QLabel('Error table')
        self.dtypesMessage = QLabel()
        lowerFrameLayout = QVBoxLayout()
        # lowerFrameLayout.addWidget(self.dtypesCombo)
        lowerFrameLayout.addWidget(frameTitle)
        lowerFrameLayout.addWidget(self.errorTable)
        lowerFrameLayout.addWidget(self.dtypesMessage)
        lowerFrame.setLayout(lowerFrameLayout)

        outerLayout.addWidget(upperFrame)
        outerLayout.addWidget(lowerFrame)

        self.propertiesWidget.setLayout(outerLayout)

    def updatePropertiesWidget(self):
        """Populate the properties dock widget with datatypes from input `Node`.

        It is called upon evaluation of the node in case columns names are different from previous evaluation"""
        if self.columnsDtype is not None:
            dtypes = self.columnsDtype.astype(str)

            # Update the columnTypeTable
            # extract types from their respective string
            dtypes = dtypes.str.extract('(' + '|'.join(TYPE_OPTIONS) + ')', expand=False)
            dtypes = dtypes.replace(np.nan, 'str')
            model = self.columnTypeTable.model()
            model.dataframe = dtypes
            self.columnTypeTable.setColumnWidth(0, 80)

            # Update the lower frame dtypesCombo box
            # self.dtypesCombo.clear()
            # self.dtypesCombo.addItems(dtypes.index)

    def updateLowerFrame(self):
        pass

    def updateValue(self, editor: QWidget):
        """Update current evaluation of the `Node`.

        Is called upon chnage of value in properties dock widget"""
        self.forcedEval()

    def evalImplementation(self, force=False):
        self.print('evalImplementation')

        # get first input
        input_node: Union[DataNode, None] = self.getInput(0)
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
        if self.columnsDtype is None or not (self.columnsDtype.index.equals(new_columns_dtype.index)):
            # Update the properties toolbar accordingly
            self.columnsDtype = new_columns_dtype
            self.updatePropertiesWidget()

        if self.columnsDtype is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        # Change column datatype to the one selected from table
        dtypes = self.columnTypeTable.model().dataframe
        # convert string values for the corresponding type
        dtypes = dtypes.apply(eval)
        self.value = self.input_val.astype(dtypes, errors='ignore')
        print(self.value.dtypes == self.columnsDtype)
        print(self.value.dtypes, self.columnsDtype)
        # TODO handle failure
        # TODO serialize / deserialize

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
