from PyQt5.QtWidgets import *
from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory
from .node_widgets import Dragger
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
        self.dragger: Union[Dragger, None] = None
        self.columns: Union[pd.Index, None] = None
        super().__init__(scene, inputs=[1], outputs=[1])

    def initPropertiesWidget(self):
        self.propertiesWidget = QWidget()
        self.propertiesWidget.setMinimumWidth(100)
        self.dragger = Dragger(inputTitle='Input columns', outputNames=['index', 'columns', 'values'])
        self.dragger.itemDropped.connect(self.forcedEval)
        layout = QVBoxLayout()
        layout.addWidget(self.dragger)
        self.propertiesWidget.setLayout(layout)

    def updatePropertiesWidget(self):
        """Update dragger attributes with columns attributes."""
        if self.columns is not None:
            self.dragger.initModel(self.columns)

    def getNodeSettings(self) -> dict:
        """Get status from dragger widget and returns them as dictionary

        Returns
        -------
        dict
            Settings from dragger attributes
        """
        return self.dragger.getStatus()

    def restoreNodeSettings(self, data: dict) -> bool:
        """Restore status of dragger widget

        Parameters
        ----------
        data: dict
            dict holding dragger widget settings under node_settings key.

        Returns
        -------
        ``bool``
        """
        assert 'node_settings' in data.keys(), 'node_settings is not in input'
        return self.dragger.restoreStatus(data['node_settings'])

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

        # Compare if new columns are the same as the old one
        if self.columns is None or not (self.columns.equals(new_columns)):
            # Update the properties toolbar accordingly
            self.columns = new_columns
            self.updatePropertiesWidget()

        if self.columns is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        # check if at least one item is present in each
        # TODO evaluate such that only two value in the settings are necessary
        widgetSettings = self.getNodeSettings()
        evaluate = True
        for key, value in widgetSettings['outputs'].items():
            print(value)
            evaluate &= len(value) >= 1
        if evaluate:
            self.print('evaluate')
            kwargs = widgetSettings['outputs']
            self.value = self.input_val.pivot_table(**kwargs)

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
