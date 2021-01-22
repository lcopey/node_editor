from PyQt5.QtWidgets import *
from ..data_node_base import DataNode
from ..data_node_graphics_base import OpGraphicsNode
from ..data_conf import NodeFactory


@NodeFactory.register()
class OpNode_PivotTable(DataNode):
    icon = 'icons/table-pivot-64.svg'
    op_title = 'Pivot Table'
    content_label = ''
    content_label_objname = 'data_node_pivot_table'

    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initPropertiesToolbar()

    def initPropertiesToolbar(self):
        # self.properties_toolbar = QWidget()
        #
        # fileLayout = QHBoxLayout()
        # self._path_text = QLineEdit()
        # self._path_text.setReadOnly(True)  # set to read only, it is modified only by selecting a path
        # self._open_file_button = QPushButton()
        # fileLayout.addWidget(QLabel('File : '))
        # fileLayout.addWidget(self._path_text)
        # fileLayout.addWidget(self._open_file_button)
        #
        # encodingLayout = QHBoxLayout()
        # encodingLayout.addWidget(QLabel('Encoding :'))
        # self._comboEncoding = QComboBox()
        # self._comboEncoding.addItem('utf-8')
        # self._comboEncoding.addItem('latin-1')
        # self._comboEncoding.currentIndexChanged.connect(self.forcedEval)
        # encodingLayout.addWidget(self._comboEncoding)
        #
        # outerLayout = QVBoxLayout()
        # outerLayout.addStretch()
        # outerLayout.addLayout(fileLayout, stretch=1)
        # outerLayout.addLayout(encodingLayout)
        # outerLayout.addStretch()
        # self.properties_toolbar.setLayout(outerLayout)
        pass
