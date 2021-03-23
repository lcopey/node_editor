from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory
import pandas as pd


@NodeFactory.register()
class OpNode_DescribeTable(DataNode):
    icon = 'resources/table-describe-64.svg'
    op_title = 'Describe'
    content_label = ''
    content_label_objname = 'data_node_describe_tables'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])

    def evalImplementation(self, force=False):
        self.print('evalImplementation')

        # get first input
        i1 = self.getInput(0)
        if not i1:
            self.setToolTip('Input is not connected')
            self.markInvalid()
            return

        # get value from input node
        df1 = i1.eval()
        if df1 is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        self.value = df1.describe()

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
