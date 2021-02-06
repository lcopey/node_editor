from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton, \
    QLineEdit, QWidget, QTableWidget, QTableView, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QIcon
import os
import pandas as pd
import csv

from typing import Any, List

# TODO implement read_csv file
# TODO Automatic discover for different modules ?
from node_editor.utils import dumpException
from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import *

DEBUG = True


@NodeFactory.register()
class OpNode_ReadCSVFile(DataNode):
    icon = 'icons/computer-folder-open-64.svg'
    op_title = 'CSV file'
    content_label = ''
    content_label_objname = 'data_node_file_read'

    GraphicsNode_class = OpGraphicsNode
    NodeContent_class = None

    def __init__(self, scene):

        super().__init__(scene, inputs=[], outputs=[1])
        self.filepath = ''
        self.file_last_modified = None

    def initPropertiesWidget(self):
        """Initialize the layout of properties DockWidget"""
        self.propertiesWidget = QWidget()
        # Import frame
        # Layout button and line edit
        fileLayout = QHBoxLayout()
        self._path_text = QLineEdit()
        self._path_text.setReadOnly(True)  # set to read only, it is modified only by selecting a path
        self._open_file_button = QPushButton()
        icon = QIcon(self.icon)
        self._open_file_button.setIcon(icon)
        self._open_file_button.clicked.connect(self.openFileDialog)

        fileLayout.addWidget(QLabel('File : '))
        fileLayout.addWidget(self._path_text)
        fileLayout.addWidget(self._open_file_button)

        # Layout encoding options
        encodingLayout = QHBoxLayout()
        encodingLayout.addWidget(QLabel('Encoding :'))
        self._comboEncoding = QComboBox()
        self._comboEncoding.addItems(['utf-8', 'latin-1'])
        self._comboEncoding.setToolTip('Encoding defines the way a text file is encoded into bytes.'
                                       'US files are usually in utf-8, european files in latin-1')
        self._comboEncoding.currentIndexChanged.connect(self.forcedEval)
        encodingLayout.addWidget(self._comboEncoding)

        importLayout = QVBoxLayout()
        importLayout.addLayout(fileLayout)
        importLayout.addLayout(encodingLayout)

        importFrame = QFrame()
        importFrame.setFrameShape(QFrame.StyledPanel)
        importFrame.setLayout(importLayout)

        # Column type frame
        # TODO change for model/view
        # populate data in the model instead of adding QTableWidgetItem
        # self.columnTypeTable = QTableWidget()
        # self.columnTypeTable.setColumnCount(2)
        # self.columnTypeTable.setHorizontalHeaderLabels(('Column', 'Type'))

        # center the widget
        outerLayout = QVBoxLayout()
        outerLayout.addStretch()
        outerLayout.addWidget(importFrame)
        # outerLayout.addWidget(self.columnTypeTable)
        outerLayout.addStretch()
        self.propertiesWidget.setLayout(outerLayout)

    def populateColumnTypeTable(self):
        """Populate the table containing the columns type with values taken from opened file.

        Returns
        -------
        None
        """
        # model = self.columnTypeTable.model()
        # model.beginResetModel()
        # if isinstance(self.value, pd.DataFrame):
        #     data = [(str(name), str(dtype)) for name, dtype in self.value.dtypes.items()]
        #     model.setDataSource(data)
        # model.endResetModel()
        pass

    def openFileDialog(self):
        subWnd = self.scene.getView().parent()
        mainWnd = subWnd.getMainWindow()

        fname, fileFilter = QFileDialog.getOpenFileName(mainWnd, 'Open csv file', '',
                                                        'CSV (*.csv);;All files (*)')
        self.print('Filename selected :', fname)
        if fname == '' and self._path_text.text() != '':
            return
        self.filepath = fname
        self._path_text.setText(self.filepath)

        # TODO Probably trigger history stamp event
        # force the evaluation of the node
        self.forcedEval()

    def evalImplementation(self):
        self.print('evalImplementation')

        if self.filepath != '':
            # store the last modified time of the file
            if not self.file_last_modified:
                self.file_last_modified = os.path.getmtime(self.filepath)

            elif self.file_last_modified == os.path.getmtime(self.filepath):
                # the file has already been loaded, simply return the values stored
                return self.value

            with open(self.filepath) as f:
                # automatically detect delimiters
                dialect = csv.Sniffer().sniff(f.read(4096), delimiters=';, \t')
                # TODO support encoding for latin-1 file
                # encoding = f.encoding
                # get encoding of the file
                encoding = self._comboEncoding.currentText()

            # load csv file
            data_frame = pd.read_csv(self.filepath, dialect=dialect, encoding=encoding)
            # by default cast some column to numeric type if possible
            data_frame = data_frame.apply(pd.to_numeric, errors='ignore')
            self.value = data_frame
            # update the table containing column type in the properties dock
            self.populateColumnTypeTable()

            self.markDirty(False)
            self.markInvalid(False)

            self.markDescendantInvalid(False)
            self.markDescendantDirty()

            self.setToolTip('')

            self.evalChildren()

        return self.value

    def serialize(self):
        # Additionally store the file path
        result = super().serialize()
        result['file_path'] = self._path_text.text()
        return result

    def deserialize(self, data, hashmap=None, restore_id=True):
        """Restore node including the file path"""
        if hashmap is None:
            hashmap = {}
        result = super().deserialize(data, hashmap, restore_id)
        self._path_text.setText(data['file_path'])
        return result
