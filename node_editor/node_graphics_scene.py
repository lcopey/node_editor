from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_scene import Scene

THEME = 'LIGHT'

colors = {'DARK':
              {'background': QColor('#393939'),
               'light': QColor("#2f2f2f"),
               'dark': QColor("#292929")},
          'LIGHT':
              {'background': QColor('#eeeeee'),
               'light': QColor('#eaeaea'),
               'dark': QColor('#e9e9e9')}}


class GraphicsScene(QGraphicsScene):
    """Implement the scene containing the backgroung"""
    itemSelected = pyqtSignal()
    itemsDeselected = pyqtSignal()

    def __init__(self, scene: 'Scene', parent=None):
        super().__init__(parent=parent)

        self.scene = scene

        # There is an issue when reconnecting edges -> mouseMove and trying to delete/remove them
        # the edges stayed in the scene in Qt, however python side was deleted
        # this caused a lot of troubles...
        #
        # I've spend months to find this sh*t!!
        #
        # https://bugreports.qt.io/browse/QTBUG-18021
        # https://bugreports.qt.io/browse/QTBUG-50691
        # Affected versions: 4.7.1, 4.7.2, 4.8.0, 5.5.1, 5.7.0 - LOL!
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        # settings
        # create background
        self.gridSize = 20
        self.gridSquare = 5

        # self._color_background = QColor('#393939')
        # self._color_light = QColor("#2f2f2f")
        # self._color_dark = QColor("#292929")
        self._color_background = colors[THEME]['background']
        self._color_light = colors[THEME]['light']
        self._color_dark = colors[THEME]['dark']

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(1)

        self.setBackgroundBrush(self._color_background)

    def setGrScene(self, width, height):
        """Define the size of the graphical scene"""
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Draw background of the graphical scene """
        super().drawBackground(painter, rect)

        # create a grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # compute all lines to be drawn
        lines_light, lines_dark = list(), list()
        # lines_light.append(QLine(0, 0, 100, 100))
        for x in range(first_left, right, self.gridSize):
            if x % (self.gridSquare * self.gridSize) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))
        for y in range(first_top, bottom, self.gridSize):
            if y % (self.gridSquare * self.gridSize) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))
        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)

    # The drag event won't be allowed until dragmoveevent is overriden
    # Otherwise, the parent won't catch the event
    def dragMoveEvent(self, QGraphicsSceneDragDropEvent):
        pass

    # def wheelEvent(self, event: 'QGraphicsSceneWheelEvent') -> None:
    #     print('wheelEvent')
    #     return
