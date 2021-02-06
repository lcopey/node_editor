from PyQt5.QtWidgets import QWidget, QGraphicsItem, QStyleOptionGraphicsItem, QGraphicsSceneHoverEvent, \
    QGraphicsSceneWheelEvent, QGraphicsSceneMouseEvent
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QRectF
from typing import TYPE_CHECKING, Optional
from .utils import dumpException

if TYPE_CHECKING:
    from .node_node import Node

THEME = 'LIGHT'

colors = {'DARK': {'status_outline': QColor("#FF00000"),
                   'status_outline_hovered': QColor("#FF37A6FF"),
                   'status_text': Qt.white},
          'LIGHT': {'status_outline': QColor("#FFc0c0c0"),
                    'status_outline_hovered': QColor("#FF06acee"),
                    'status_text': Qt.black}
          }


class GraphicsStatus(QGraphicsItem):
    def __init__(self, node: 'Node' = None):
        super().__init__(parent=node.grNode)
        self.node = node
        self.radius = 10
        self.outline_width = 1

        self._hovered = False
        self.setAcceptHoverEvents(True)

        self.initAssets()

    def initAssets(self):
        self._color_outline = colors[THEME]['status_outline']
        self._color_outline_hovered = colors[THEME]['status_outline_hovered']

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(self.outline_width)
        self._pen_hovered = QPen(self._color_outline_hovered)
        self._pen_hovered.setWidth(self.outline_width + 2)
        self._pen_text = QPen(colors[THEME]['status_text'])

        self._invalid_brush = QBrush(QColor('#ed1d25'))
        self._valid_brush = QBrush(QColor('#00a651'))
        self._dirty_brush = QBrush(QColor('#ffe543'))

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._hovered = True
        self.node.grNode.enableHoverEvents(False)
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._hovered = False
        self.node.grNode.enableHoverEvents(True)
        self.update()
        super().hoverLeaveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """Override's Qt mouse release event.
        # TODO Trigger a context menu with evaluation option ?

        Parameters
        ----------
        event: QGraphicsSceneMouseEvent
            Event triggering the mouseReleaseEvent
        """
        pass

    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent') -> None:
        pass

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: Optional[QWidget] = ...) -> None:
        # painting circle
        if self.node.isInvalid():
            painter.setBrush(self._invalid_brush)
            text = '!'
        elif self.node.isDirty():
            painter.setBrush(self._dirty_brush)
            text = '?'
        else:
            painter.setBrush(self._valid_brush)
            text = "\N{CHECK MARK}"

        painter.setPen(self._pen if not self._hovered else self._pen_hovered)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

        # Text in the status
        painter.setPen(self._pen_text)
        font = QFont('Ubuntu', self.radius * 2 - 6)
        fm = QFontMetrics(font)
        painter.setFont(font)
        painter.drawText(-fm.width(text) / 2, fm.height() / 2 - 4, text)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.radius - self.outline_width,
                      -self.radius - self.outline_width,
                      2 * (self.radius + self.outline_width),
                      2 * (self.radius + self.outline_width))
