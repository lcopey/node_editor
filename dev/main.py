import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from typing import Optional


from graphics import QGraphicsResizableRectItem


def main():
    app = QApplication(sys.argv)

    grview = QGraphicsView()
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 680, 459)
    grview.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | \
                          QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
    grview.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    scene.addPixmap(QPixmap('01.png'))
    grview.setScene(scene)

    item = QGraphicsResizableRectItem(100, 100, 0, 0, 180, 240)

    scene.addItem(item)
    grview.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    grview.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
