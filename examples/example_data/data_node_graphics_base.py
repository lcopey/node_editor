from node_editor.node_graphics_node import GraphicsNode
from node_editor.node_node import Node


class VizGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None, resizeable=True, min_height=240, min_width=180):
        super().__init__(node=node, parent=parent, resizeable=True, min_height=min_height, min_width=min_width)

    def initSizes(self):
        # Diverse parameters for drawing
        super().initSizes()
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

        self.min_width = self.width = 160
        self.min_height = self.height = 74


class OpGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None, resizeable=True, min_height=240, min_width=180):
        super().__init__(node=node, parent=parent, resizeable=False, min_height=min_height, min_width=min_width)
        # TODO subclass paint as a circle
        # TODO subclass getSocketPosition

    def initSizes(self):
        # Diverse parameters for drawing
        super().initSizes()
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

        self.min_width = self.width = 100
        self.min_height = self.height = 54
