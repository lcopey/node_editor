from ..data_node_base import DataNode, OpGraphicsNode
from ..data_conf import NodeFactory


@NodeFactory.register()
class OpNode_PivotTable(DataNode):
    icon = 'icons/table-pivot-64.svg'
    op_title = 'Pivot Table'
    content_label = ''
    content_label_objname = 'data_node_pivot_table'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
