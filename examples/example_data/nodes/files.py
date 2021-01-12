# TODO implement read_csv file
# TODO Automatic discover for different modules ?
from ..data_node_base import DataNode, VizGraphicsNode
from ..data_conf import NodeType, register_node

DEBUG = True

@register_node(NodeType.OP_NODE_FILE_READ)
class DataNode_ReadFile(DataNode):
    icon = 'icons/in.png'
    op_code = NodeType.OP_NODE_FILE_READ
    op_title = 'FileRead'
    content_label = ''
    content_label_objname = 'data_node_file_read'

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.eval()
        self.grNode.updateLayout()

    def initInnerClasses(self):
        # self.content = DataTableContent(self)
        self.grNode = VizGraphicsNode(self)
        self.print('initInnerClasses done')
        # self.content.edit.textChanged.connect(self.onInputChanged)

    def print(self, *args):
        if DEBUG: print('>DataNode_File : ', *args)
    #
    # def evalImplementation(self):
    #     u_value = self.content.edit.text()
    #     s_value = int(u_value)
    #     self.value = s_value
    #
    #     self.markDirty(False)
    #     self.markInvalid(False)
    #
    #     self.markDescendantInvalid(False)
    #     self.markDescendantDirty()
    #
    #     self.grNode.setToolTip("")
    #
    #     self.evalChildren()
    #
    #     return self.value
