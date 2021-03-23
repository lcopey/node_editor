from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory


@NodeFactory.register()
class OpNode_MergeTable(DataNode):
    icon = 'resources/table-merge-64.svg'
    op_title = 'Merge'
    content_label = ''
    content_label_objname = 'data_node_merge_tables'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1])
