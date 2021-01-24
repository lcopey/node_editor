import sys
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QWidget, QLineEdit, QApplication, QTableView, QVBoxLayout, QLineEdit, QComboBox
from PyQt5.QtCore import pyqtSignal, QSize


class FilterHeader(QHeaderView):
    filterActivated = pyqtSignal()

    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self._editors = []
        self._padding = 4
        # self.setStretchLastSection(True)
        # self.setResizeMode(QHeaderView.Stretch)
        self.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.setSortIndicatorShown(False)
        self.sectionResized.connect(self.adjustPositions)
        parent.horizontalScrollBar().valueChanged.connect(self.adjustPositions)

    def setFilterBoxes(self, column_count: int):
        """Define widgets in the header

        Parameters
        ----------
        column_count : int
            count of columns in current QTableView
        """
        # Empty self._editors
        while self._editors:
            editor = self._editors.pop()
            editor.deleteLater()

        # Create new widgets according to current count of columns
        for index in range(column_count):
            # Define QLineEdit
            editor = QLineEdit(self)
            editor.setPlaceholderText('Filter')
            # On pressing enter, emit a new filterActivated event
            editor.returnPressed.connect(self.filterActivated.emit)
            if not editor.isVisible():
                editor.show()
            self._editors.append(editor)
        # Adjust position of the widgets
        self.adjustPositions()

    def adjustPositions(self):
        """Adjust position of the Widgets in the header
        """
        for index, editor in enumerate(self._editors):
            height = editor.sizeHint().height()
            editor.move(self.sectionPosition(index) - self.offset() + 2, height + (self._padding // 2))
            editor.resize(self.sectionSize(index), height)

    def sizeHint(self) -> QSize:
        """Adjust the sizeHint of the header to account for the header + QLineEdit

        Returns
        -------

        """
        size = super().sizeHint()
        if self._editors:
            height = self._editors[0].sizeHint().height()
            size.setHeight(size.height() + height + self._padding)
        return size

    def updateGeometries(self):
        if self._editors:
            height = self._editors[0].sizeHint().height()
            self.setViewportMargins(0, 0, 0, height + self._padding)
        else:
            self.setViewportMargins(0, 0, 0, 0)
        super().updateGeometries()
        self.adjustPositions()

    def getFilterTextAtIndex(self, index: int):
        """Get filter text

        Parameters
        ----------
        index : int
            `index` of the widget to get the text from

        Returns
        -------
        str
            text hold by the header section at `index`
        """
        if 0 <= index < len(self._editors):
            return self._editors[index].text()
        return ''

    def setFilterText(self, index, text):
        """

        Parameters
        ----------
        index
        text

        Returns
        -------

        """
        if 0 <= index < len(self._editors):
            self._editors[index].setText(text)

    def clearFilters(self):
        """

        Returns
        -------

        """
        for editor in self._editors:
            editor.clear()


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.view = QTableView()
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        header = FilterHeader(self.view)
        self.view.setHorizontalHeader(header)
        model = QtGui.QStandardItemModel(self.view)
        model.setHorizontalHeaderLabels('One Two Three Four Five'.split())
        self.view.setModel(model)
        header.setFilterBoxes(model.columnCount())
        header.filterActivated.connect(self.handleFilterActivated)

    def handleFilterActivated(self):
        header = self.view.horizontalHeader()
        for index in range(header.count()):
            print((index, header.filterText(index)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.setGeometry(600, 100, 600, 300)
    window.show()
    sys.exit(app.exec_())
