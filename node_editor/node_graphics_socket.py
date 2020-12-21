from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import typing

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_socket import Socket

OUTPUT_SOCKET = 0
INPUT_SOCKET_1 = 1
INPUT_SOCKET_2 = 2
INPUT_SOCKET_3 = 3
INPUT_SOCKET_4 = 4


class QNEGraphicsSocket(QGraphicsItem):
    def __init__(self, socket: 'Socket', socket_type=1):
        super().__init__(socket.node.grNode)
        self.socket = socket

        self.radius = 6
        self.outline_width = 1
        # self._colors = [
        #     QColor('#FFFF7700'),
        #     QColor('#FF52e220'),
        #     QColor('#FF0056a6'),
        #     QColor('#FFa86db1'),
        #     QColor('#FFb54747'),
        #     QColor('#FFdbe220'),
        # ]
        self._colors = [QColor('#FFFF7F0E'),
                        QColor('#FF1F77B4'),
                        QColor('#Ff2CA02C'),
                        QColor('#FFD62728'),
                        QColor('#FF9467BD'),
                        QColor('#FF8C564B'),
                        QColor('#FFE377C2'),
                        QColor('#FF7F7F7F'),
                        QColor('#FFBCBD22'),
                        QColor('#FF17BECF')]
        self._color_background = self._colors[socket_type]
        self._color_outline = QColor('#FF000000')

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(self.outline_width)
        self._brush = QBrush(self._color_background)

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius,
                            2 * self.radius, 2 * self.radius)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.radius - self.outline_width,
                      -self.radius - self.outline_width,
                      2 * (self.radius + self.outline_width),
                      2 * (self.radius + self.outline_width))
