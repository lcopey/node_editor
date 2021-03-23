import enum

LISTBOX_MIMETYPE = "application/x-item"


class NodeFactory:
    """Register of nodes create in sumodules nodes.

    Update a dictionary with the class name and the reference to constructor"""
    registered_nodes = {}

    @staticmethod
    def get_nodes():
        """Get registered nodes"""
        return list(NodeFactory.registered_nodes.keys())

    @staticmethod
    def _register_node(class_reference):
        op_code = class_reference.__name__
        if op_code in NodeFactory.registered_nodes:
            raise InvalidNodeRegistration(
                "Duplicate node registration of {}. There is already {}".format(op_code,
                                                                                NodeFactory.registered_nodes[op_code]))
        NodeFactory.registered_nodes[op_code] = class_reference

    @staticmethod
    def register():
        """Decorator registering the node in NodeFactory"""

        def decorator(original_class):
            NodeFactory._register_node(original_class)
            return original_class

        return decorator

    @staticmethod
    def from_op_code(op_code):
        """Return class reference corresponding to op_code"""
        if op_code not in NodeFactory.registered_nodes:
            raise OpCodeNotRegistered('OpCode {} is not registered'.format(op_code))
        return NodeFactory.registered_nodes[op_code]


class ConfException(Exception): pass


class InvalidNodeRegistration(ConfException): pass


class OpCodeNotRegistered(ConfException): pass
