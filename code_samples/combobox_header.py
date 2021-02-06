from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QEvent, QObject
import numpy as np


class HeaderViewFilter(QObject):
    def __init__(self, header, parent=None, *args):
        super(HeaderViewFilter, self).__init__(parent, *args)
        self.header = header

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseMove:
            logicalIndex = self.header.logicalIndexAt(event.pos())
            print(logicalIndex)


class HorizontalHeader(QtWidgets.QHeaderView):
    def __init__(self, values, parent=None):
        super(HorizontalHeader, self).__init__(QtCore.Qt.Horizontal, parent)
        self.setSectionsMovable(True)
        # self.setStretchLastSection(True)
        self._padding = 4
        self.line_edits = []
        self.sectionResized.connect(self.handleSectionResized)
        self.sectionMoved.connect(self.handleSectionMoved)
        self.setSectionsMovable(True)
        self.setSectionsClickable(True)

        self.setSortIndicatorShown(True)

        # try:
        #     self.evenFilter = HeaderViewFilter(self)
        #     self.setMouseTracking(True)
        #
        #     self.installEventFilter(self.evenFilter)
        # except Exception as e:
        #     print(e)

    def showEvent(self, event):
        for i in range(self.count()):
            if i < len(self.line_edits):
                edit = self.line_edits[i]
                edit.clear()
                edit.addItems(["Variable", "Timestamp"])
            else:
                edit = QtWidgets.QLineEdit(self)
                # dtypesCombo.setEditable(True)
                # dtypesCombo.addItems(["Variable", "Timestamp"])
                self.line_edits.append(edit)

            # if i == 0:
            edit.setGeometry(*self.getInnerWidgetGeometry(i))
            edit.show()

        if len(self.line_edits) > self.count():
            for i in range(self.count(), len(self.line_edits)):
                self.line_edits[i].deleteLater()

        super(HorizontalHeader, self).showEvent(event)

    def sizeHint(self):
        size = super().sizeHint()
        if self.line_edits:
            height = self.line_edits[0].sizeHint().height()
            size.setHeight(size.height() + height + self._padding)
        return size

    def getInnerWidgetGeometry(self, i):
        height = self.line_edits[i].sizeHint().height()
        return self.sectionViewportPosition(i), self.height(), self.sectionSize(i) - 5, self.height() + height

    def fixComboPositions(self):
        for i in range(self.count()):
            self.line_edits[i].setGeometry(*self.getInnerWidgetGeometry(i))

    def handleSectionResized(self, i):
        for i in range(self.count()):
            j = self.visualIndex(i)
            logical = self.logicalIndex(j)
            self.line_edits[i].setGeometry(self.sectionViewportPosition(logical), 0, self.sectionSize(logical) - 4,
                                           self.height())

    def handleSectionMoved(self, i, oldVisualIndex, newVisualIndex):
        for i in range(min(oldVisualIndex, newVisualIndex), self.count()):
            logical = self.logicalIndex(i)
            self.line_edits[i].setGeometry(self.sectionViewportPosition(logical), 0, self.sectionSize(logical) - 5,
                                           self.height())


class TableWidget(QtWidgets.QTableWidget):
    def __init__(self, *args, **kwargs):
        super(TableWidget, self).__init__(*args, **kwargs)
        header = HorizontalHeader(self)
        self.setHorizontalHeader(header)

    def scrollContentsBy(self, dx, dy):
        super(TableWidget, self).scrollContentsBy(dx, dy)
        if dx != 0:
            self.horizontalHeader().fixComboPositions()


class App(QtWidgets.QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.data = np.random.rand(10, 10)
        self.createTable()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        self.show()

    def createTable(self):
        self.header = []
        self.table = TableWidget(*self.data.shape)
        for i, row_values in enumerate(self.data):
            for j, value in enumerate(row_values):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
