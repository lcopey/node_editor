from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

THEME = 'LIGHT'

colors = {'DARK':
              {'cutline_color': Qt.white},
          'LIGHT':
              {'cutline_color': Qt.darkGray}
          }


class CutLine(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.line_points = []

        self._pen = QPen(colors[THEME]['cutline_color'])
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)  # set in front

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        # poly = QPolygonF(self.line_points)
        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))
        return path

    def paint(self, painter: QPainter, QStyleOptionGraphicsItem, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)
