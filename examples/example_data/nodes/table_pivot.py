from ..data_node_base import DataNode, OpGraphicsNode
from ..data_conf import NodeFactory


@NodeFactory.register()
class OpNode_PivotTable(DataNode):
    icon = 'icons/table-64-colored.svg'
    op_title = 'PivotTable'
    content_label = ''
    content_label_objname = 'data_node_pivot_table'

    GraphicsNode_class = OpGraphicsNode

