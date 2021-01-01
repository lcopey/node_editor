from ..calc_conf import *
from ..calc_node_base import *
from node_editor.utils import dumpException


@register_node(OP_NODE_ADD)
class CalcNode_Add(CalcNode):
    icon = 'icons/add.png'
    op_code = OP_NODE_ADD
    op_title = 'Add'
    content_label = '+'
    content_label_objname = 'calc_node_bg'

    def evalOperation(self, i1, i2):
        return i1 + i2


@register_node(OP_NODE_SUB)
class CalcNode_Sub(CalcNode):
    icon = 'icons/sub.png'
    op_code = OP_NODE_SUB
    op_title = 'Substract'
    content_label = '-'
    content_label_objname = 'calc_node_bg'

    def evalOperation(self, i1, i2):
        return i1 - i2


@register_node(OP_NODE_MUL)
class CalcNode_Mul(CalcNode):
    icon = 'icons/mul.png'
    op_code = OP_NODE_MUL
    op_title = 'Multiply'
    content_label = '*'
    content_label_objname = 'calc_node_mul'

    def evalOperation(self, i1, i2):
        return i1 * i2


@register_node(OP_NODE_DIV)
class CalcNode_Div(CalcNode):
    icon = 'icons/divide.png'
    op_code = OP_NODE_DIV
    op_title = 'Divide'
    content_label = '/'
    content_label_objname = 'calc_node_div'

    def evalOperation(self, i1, i2):
        return i1 / i2

# register by function call
# register_node_now(OP_NODE_ADD, CalcNode_Add)
