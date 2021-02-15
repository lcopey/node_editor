from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory
import pandas as pd


@NodeFactory.register()
class OpNode_ConcatTable(DataNode):
    icon = 'icons/table-concat-64.png'
    op_title = 'Concatenate'
    content_label = ''
    content_label_objname = 'data_node_concatenates_tables'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1])

    def evalImplementation(self, force=False):
        self.print('evalImplementation')

        # get first input
        i1 = self.getInput(0)
        i2 = self.getInput(1)
        if not i1 or not i2:
            self.setToolTip('Input is not connected')
            self.markInvalid()
            return

        # get value from input node
        df1 = i1.eval()
        df2 = i2.eval()
        if df1 is None:
            self.setToolTip('First input is NaN')
            self.markInvalid()
            return
        elif df2 is None:
            self.setToolTip('Second input is NaN')
            self.markInvalid()
            return


        self.value = pd.concat([df1, df2])

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value
