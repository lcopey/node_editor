from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QTextEdit, QPushButton, QLineEdit, \
    QFileDialog, QComboBox, QFrame
import os
import pandas as pd
import csv

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
    # op_code = NodeType.OP_NODE_FILE_READ
    op_title = 'CSV file'
    content_label = ''
    content_label_objname = 'data_node_file_read'

    GraphicsNode_class = OpGraphicsNode
    NodeContent_class = None

    def __init__(self, scene):

        super().__init__(scene, inputs=[], outputs=[1])
        self.filepath = ''
        self.file_last_modified = None
        self.grNode.updateLayout()

    def initPropertiesToolbar(self):
        """Initialize the layout of properties DockWidget"""
        self.properties_toolbar = QWidget()

        fileLayout = QHBoxLayout()
        self._path_text = QLineEdit()
        self._path_text.setReadOnly(True)  # set to read only, it is modified only by selecting a path
        self._open_file_button = QPushButton()
        self._open_file_button.clicked.connect(self.openFileDialog)
        fileLayout.addWidget(QLabel('File : '))
        fileLayout.addWidget(self._path_text)
        fileLayout.addWidget(self._open_file_button)

        encodingLayout = QHBoxLayout()
        encodingLayout.addWidget(QLabel('Encoding :'))
        self._comboEncoding = QComboBox()
        self._comboEncoding.addItem('utf-8')
        self._comboEncoding.addItem('latin-1')
        self._comboEncoding.currentIndexChanged.connect(self.forcedEval)
        encodingLayout.addWidget(self._comboEncoding)

        outerLayout = QVBoxLayout()
        outerLayout.addStretch()
        outerLayout.addLayout(fileLayout, stretch=1)
        outerLayout.addLayout(encodingLayout)
        outerLayout.addStretch()
        self.properties_toolbar.setLayout(outerLayout)

    def getPropertiesToolbar(self):
        self.print('getPropertiesToolbar')
        return self.properties_toolbar

    def openFileDialog(self):
        subWnd = self.scene.getView().parent()
        mainWnd = subWnd.getMainWindow()

        fname, filter = QFileDialog.getOpenFileName(mainWnd, 'Open csv file', '',
                                                    'CSV (*.csv);;All files (*)')
        self.print('Filename selected :', fname)
        if fname == '' and self._path_text.text() != '':
            return
        self.filepath = fname
        self._path_text.setText(self.filepath)

        # TODO Probably trigger history stamp event
        # force the evaluation of the node
        self.forcedEval()

    def forcedEval(self):
        self.eval(force=True)

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
            data_frame = data_frame.apply(pd.to_numeric, errors='ignore')
            self.value = data_frame

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

    def deserialize(self, data, hashmap={}, restore_id=True):
        """Restore node including the file path"""
        result = super().deserialize(data, hashmap, restore_id)
        self._path_text.setText(data['file_path'])
        return result
