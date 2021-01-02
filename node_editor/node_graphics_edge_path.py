from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import QPointF
import math

EDGE_CP_ROUNDNESS = 100


class GraphicsEdgePathBase:
    """Base class for calculating the graphics pathh to draw for a graphics Edge"""

    def __init__(self, owner: 'QNEGraphicsEdge'):
        # keep the reference to owner GraphicsEdge class
        self.owner = owner

    def calcPath(self):
        """Calculate the path connection

        Returns
        -------
        QPainterPath or None
            `QPainterPath` of the edge to draw

        """

        return None


class QNEGraphicsEdgePathDirect(GraphicsEdgePathBase):
    def calcPath(self):
        """Compute linear path from source to destination"""
        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))
        path.lineTo(self.owner.posDestination[0], self.owner.posDestination[1])
        return path


class QNEGraphicsEdgePathBezier(GraphicsEdgePathBase):
    def calcPath(self):
        """Compute bezier curves from source to destination"""
        s = self.owner.posSource
        d = self.owner.posDestination

        dist = (d[0] - s[0]) * 0.5

        # Compute control point
        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.owner.edge.start_socket is not None:
            ssin = self.owner.edge.start_socket.is_input
            ssout = self.owner.edge.start_socket.is_output
            sspos = self.owner.edge.start_socket.position
            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = ((s[1] - d[1]) / (math.fabs(s[1] - d[1]) + 1e-8)) * EDGE_CP_ROUNDNESS
                cpy_s = ((d[1] - s[1]) / (math.fabs(s[1] - d[1]) + 1e-8)) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))
        path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d,
                     self.owner.posDestination[0], self.owner.posDestination[1])
        return path
