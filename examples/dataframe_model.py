import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView, QHeaderView, QTableWidget
from PyQt5.QtCore import QAbstractTableModel, Qt, QAbstractItemModel, pyqtSignal, QByteArray, QDataStream, QIODevice, \
    QMimeData
from PyQt5.QtGui import QDrag


class DataframeView(QTableView):
    def __init__(self, parent=None, dataframe: pd.DataFrame = None):
        super(DataframeView, self).__init__(parent)
        header = MyHeader()
        # self.setHorizontalHeader(header)
        self.horizontalHeader().setSectionsMovable(True)
        self.verticalHeader().setSectionsMovable(True)
        if dataframe is not None:
            self.setDataFrame(dataframe)

    def setDataFrame(self, dataframe: pd.DataFrame):
        dataframe_model = DataframeModel(dataframe=dataframe)
        super().setModel(dataframe_model)


class MyHeader(QHeaderView):
    MimeType = 'application/x-qabstractitemmodeldatalist'
    columnsChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self._dragstartpos = None

    def encodeMimeData(self, items):
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        for column, label in items:
            stream.writeInt32(0)
            stream.writeInt32(column)
            stream.writeInt32(2)
            stream.writeInt32(int(Qt.DisplayRole))
            stream.writeQVariant(label)
            stream.writeInt32(int(Qt.UserRole))
            stream.writeQVariant(column)
        mimedata = QMimeData()
        mimedata.setData(MyHeader.MimeType, data)
        return mimedata

    def decodeMimeData(self, mimedata):
        data = []
        stream = QDataStream(mimedata.data(MyHeader.MimeType))
        while not stream.atEnd():
            row = stream.readInt32()
            column = stream.readInt32()
            item = {}
            for count in range(stream.readInt32()):
                key = stream.readInt32()
                item[key] = stream.readQVariant()
            data.append([item[Qt.UserRole], item[Qt.DisplayRole]])
        return data

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragstartpos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton and
                self._dragstartpos is not None and
                (event.pos() - self._dragstartpos).manhattanLength() >=
                QApplication.startDragDistance()):
            column = self.logicalIndexAt(self._dragstartpos)
            data = [column, self.model().headerData(column, Qt.Horizontal)]
            self._dragstartpos = None
            drag = QDrag(self)
            drag.setMimeData(self.encodeMimeData([data]))
            action = drag.exec(Qt.MoveAction)
            if action != Qt.IgnoreAction:
                self.setColumnHidden(column, True)

    def dropEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasFormat(MyHeader.MimeType):
            if event.source() is not self:
                for column, label in self.decodeMimeData(mimedata):
                    self.setColumnHidden(column, False)
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.ignore()
        else:
            super().dropEvent(event)

    def setColumnHidden(self, column, hide=True):
        count = self.count()
        if 0 <= column < count and hide != self.isSectionHidden(column):
            if hide:
                self.hideSection(column)
            else:
                self.showSection(column)
            self.columnsChanged.emit(count - self.hiddenSectionCount())


class DataframeModel(QAbstractTableModel):

    def __init__(self, dataframe: pd.DataFrame):
        QAbstractTableModel.__init__(self)
        self._data = dataframe

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            value = self._data.iloc[index.row(), index.column()]
            if role == Qt.DisplayRole:
                return str(value)
            elif role == Qt.TextAlignmentRole:
                return self._align(value)
            # elif role == Qt.DecorationRole

        return None

    def _align(self, value):
        if pd.api.types.is_numeric_dtype(value):
            return Qt.AlignVCenter + Qt.AlignRight
        else:
            return Qt.AlignVCenter + Qt.AlignLeft

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == Qt.DisplayRole:
            if Qt_Orientation == Qt.Horizontal:
                return self._data.columns[p_int]
            if Qt_Orientation == Qt.Vertical:
                return self._data.index[p_int]
        return None


if __name__ == '__main__':
    df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                       'b': [100, 200, 300],
                       'c': ['a', 'ba', 'c']})

    app = QApplication(sys.argv)
    # model = DataframeModel(df)
    # view = QTableView()
    # view.setModel(model)
    view = DataframeView(dataframe=df)
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())
