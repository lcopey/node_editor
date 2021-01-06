from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import typing

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_socket import Socket

OUTPUT_SOCKET = 1
INPUT_SOCKET_1 = 2
INPUT_SOCKET_2 = 3
INPUT_SOCKET_3 = 4
INPUT_SOCKET_4 = 5

SOCKET_COLOR = [QColor('#FFFF7F0E'),
                QColor('#FF1F77B4'),
                QColor('#Ff2CA02C'),
                QColor('#FFD62728'),
                QColor('#FF9467BD'),
                QColor('#FF8C564B'),
                QColor('#FFE377C2'),
                QColor('#FF7F7F7F'),
                QColor('#FFBCBD22'),
                QColor('#FF17BECF')]


class QNEGraphicsSocket(QGraphicsItem):
    def __init__(self, socket: 'Socket'):
        super().__init__(socket.node.grNode)
        self.socket = socket

        self.isHighlighted = False

        self.radius = 6
        self.outline_width = 1
        self.initAssets()

    @property
    def socket_type(self):
        return self.socket.socket_type

    def initAssets(self):
        self._color_background = self.getSocketColor(self.socket_type)
        self._color_outline = QColor('#FF000000')
        self._color_highlight = QColor('#FF37A6FF')

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(self.outline_width)
        self._pen_highlight = QPen(self._color_highlight)
        self._pen_highlight.setWidthF(2.)
        self._brush = QBrush(self._color_background)

    def changeSocketType(self):
        """Change the `Socket` Type.

        Change are exclusively graphical."""
        self._color_background = self.getSocketColor(self.socket_type)
        self._brush = QBrush(self._color_background)
        self.update()

    def getSocketColor(self, key):
        """Returns the ``QColor`` for this ``key``

        Parameters
        ----------
        key : ```str``` or ```int```
            Either a string referencing a ``QColor`` or an integer

        Returns
        -------
        ``QColor``

        """
        if type(key) == int:
            return SOCKET_COLOR[key]
        elif type(key) == str:
            return QColor(key)
        return Qt.transparent

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen if not self.isHighlighted else self._pen_highlight)
        painter.drawEllipse(-self.radius, -self.radius,
                            2 * self.radius, 2 * self.radius)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.radius - self.outline_width,
                      -self.radius - self.outline_width,
                      2 * (self.radius + self.outline_width),
                      2 * (self.radius + self.outline_width))
