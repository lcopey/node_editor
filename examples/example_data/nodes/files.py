from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QTextEdit, QPushButton, QLineEdit, \
    QFileDialog
import pandas as pd
import csv

# TODO implement read_csv file
# TODO Automatic discover for different modules ?
from node_editor.utils import dumpException
from ..data_node_base import DataNode, OpGraphicsNode
from ..data_conf import NodeType, register_node

DEBUG = True


@register_node(NodeType.OP_NODE_FILE_READ)
class DataNode_ReadFile(DataNode):
    icon = 'icons/computer-folder-open-64.svg'
    op_code = NodeType.OP_NODE_FILE_READ
    op_title = 'FileRead'
    content_label = ''
    content_label_objname = 'data_node_file_read'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.initPropertiesToolbar()
        self.eval()
        self.grNode.updateLayout()

        self.filepath = ''

    def initPropertiesToolbar(self):
        self.properties_toolbar = QWidget()

        topLayout = QFormLayout()
        topLayout.addRow(QLabel('Read csv file : '))

        optionsLayout = QHBoxLayout()
        self._path_text = QLineEdit()
        self._open_file_button = QPushButton()
        self._open_file_button.clicked.connect(self.openFileDialog)
        optionsLayout.addWidget(self._path_text)
        optionsLayout.addWidget(self._open_file_button)

        outerLayout = QVBoxLayout()
        outerLayout.addStretch()
        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(optionsLayout, stretch=1)
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
        self._path_text.setText(fname)
        # if connected, evaluate the node
        # TODO add validate button ?
        # TODO bug when multiple nodes are connected, evaluate only the first children
        # TODO Probably trigger history stamp event
        if self.getOutputs(0):
            self.evalChildren()

    def evalImplementation(self):
        self.print('evalImplementation')
        # get filename from
        file_path = self._path_text.text()

        data_frame = None
        if file_path != '':
            with open(file_path) as f:
                # automatically detect delimiters
                dialect = csv.Sniffer().sniff(f.read(4096), delimiters=';, \t')
                encoding = f.encoding
            data_frame = pd.read_csv(file_path, dialect=dialect, encoding=encoding)

        return data_frame

    def serialize(self):
        # Additionally store the file path
        result = super().serialize()
        result['file_path'] = self._path_text.text()
        return result

    def deserialize(self, data, hashmap={}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        self._path_text.setText(data['file_path'])
        return result
