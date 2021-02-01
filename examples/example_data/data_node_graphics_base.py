from node_editor.node_graphics_node import GraphicsNode
from node_editor.node_node import Node


class VizGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None):
        super().__init__(node=node, parent=parent, resizeable=True, min_width=160, width=160, min_height=74, height=74)
        # Diverse parameters for drawing
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

class OpGraphicsNode(GraphicsNode):
    # TODO subclass paint as a circle
    # TODO subclass getSocketPosition
    def __init__(self, node: 'Node', parent=None):
        super().__init__(node=node, parent=parent, resizeable=False, min_width=100, width=100, min_height=54, height=54)
        # Diverse parameters for drawing
        super().initSizes(resizeable=False, min_width=100, width=100, min_height=54, height=54)
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10


