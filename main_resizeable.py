import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
# from handle_rect import GraphicsRectItem
from node_editor.graphics import QGraphicsResizableRectItem


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
    # item = GraphicsRectItem()
    scene.addItem(item)

    grview.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    grview.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
