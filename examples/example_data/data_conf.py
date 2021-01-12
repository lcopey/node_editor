import enum

LISTBOX_MIMETYPE = "application/x-item"

# TODO Create a node factory

class NodeType(enum.IntEnum):
    OP_NODE_TABLE = 1
    OP_NODE_FILE_READ = 2
    # OP_NODE_ADD = 3
    # OP_NODE_SUB = 4
    # OP_NODE_MUL = 5
    # OP_NODE_DIV = 6
    @classmethod
    def register(cls, op_code_name, op_code):
        setattr(cls, op_code_name, op_code)


DATA_NODES = {}


class ConfException(Exception): pass


class InvalidNodeRegistration(ConfException): pass


class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference):
    """Register node"""
    if op_code in DATA_NODES:
        raise InvalidNodeRegistration(
            "Duplicate node registration of {}. There is already {}".format(op_code, DATA_NODES[op_code]))
    DATA_NODES[op_code] = class_reference


def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class

    return decorator


def get_call_from_opcode(op_code):
    if op_code not in DATA_NODES:
        raise OpCodeNotRegistered('OpCode {} is not registered'.format(op_code))
    return DATA_NODES[op_code]


# import all nodes register them
from .nodes import *
