from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory
import pandas as pd


@NodeFactory.register()
class OpNode_TransposeTable(DataNode):
    icon = 'icons/table-transpose-64.svg'
    op_title = 'Transpose'
    content_label = ''
    content_label_objname = 'data_node_transpose_tables'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])

    def evalImplementation(self):
        self.print('evalImplementation')

        self.markDirty(False)
        self.markInvalid(False)

        # get first input
        i1 = self.getInput(0)
        if not i1:
            self.setToolTip('Input is not connected')
            self.markInvalid()
            return

        # get value from input node
        df1 = i1.eval()
        if df1 is None:
            self.setToolTip('First input is NaN')
            self.markInvalid()
            return

        self.value = df1.T

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
