import enum

LISTBOX_MIMETYPE = "application/x-item"

class NodeType(enum.IntEnum):
    OP_NODE_INPUT = 1
    OP_NODE_OUTPUT = 2
    OP_NODE_ADD = 3
    OP_NODE_SUB = 4
    OP_NODE_MUL = 5
    OP_NODE_DIV = 6

CALC_NODES = {}


class ConfException(Exception): pass


class InvalidNodeRegistration(ConfException): pass


class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference):
    """Register node"""
    if op_code in CALC_NODES:
        raise InvalidNodeRegistration(
            "Duplicate node registration of {}. There is already {}".format(op_code, CALC_NODES[op_code]))
    CALC_NODES[op_code] = class_reference


def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class

    return decorator


def get_call_from_opcode(op_code):
    if op_code not in CALC_NODES:
        raise OpCodeNotRegistered('OpCode {} is not registered'.format(op_code))
    return CALC_NODES[op_code]

# import all nodes register them
from .nodes import *
