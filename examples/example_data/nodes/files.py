from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QAbstractTableModel, QSize
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

DEBUG = False


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

    def _file_UI(self) -> QLayout:
        outer_layout = QVBoxLayout()
        # Layout button and line edit
        layout = QHBoxLayout()
        self._path_text = QLineEdit()
        self._path_text.setReadOnly(True)  # set to read only, it is modified only by selecting a path
        self._open_file_button = QPushButton()
        icon = QIcon(self.icon)
        self._open_file_button.setIcon(icon)
        self._open_file_button.clicked.connect(self.openFileDialog)

        layout.addWidget(QLabel('File : '))
        layout.addWidget(self._path_text)
        layout.addWidget(self._open_file_button)
        outer_layout.addLayout(layout)

        # Layout encoding options
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Encoding :'))
        self._combo_encoding = QComboBox()
        self._combo_encoding.addItems(['utf-8', 'latin-1'])
        self._combo_encoding.setToolTip('Encoding defines the way a text file is encoded into bytes.'
                                        'US files are usually in utf-8, european files in latin-1')
        self._combo_encoding.currentIndexChanged.connect(self.forcedEval)
        layout.addWidget(self._combo_encoding)
        outer_layout.addLayout(layout)
        return outer_layout

    def _idx_UI(self):
        outer_layout = QGridLayout()

        self._idx_spinbox = QSpinBox()
        # self._idx_spinbox.setFixedWidth(36)
        outer_layout.addWidget(QLabel('Col #'), 0, 0)
        outer_layout.addWidget(self._idx_spinbox, 1, 0)

        bttn_layout = QVBoxLayout()
        self._idx_add_btn = QPushButton()
        self._idx_add_btn.setText('>')
        self._idx_add_btn.clicked.connect(self.onIdxAddBtnClicked)
        self._idx_rem_btn = QPushButton()
        self._idx_rem_btn.setText('<')
        # self._idx_rem_btn.setFixedWidth(12)
        self._idx_rem_btn.clicked.connect(self.onIdxRemBtnClicked)
        bttn_layout.addWidget(self._idx_add_btn)
        bttn_layout.addWidget(self._idx_rem_btn)
        outer_layout.addLayout(bttn_layout, 1, 1)

        self._idx_list = QListWidget()
        self._idx_list.setFixedSize(QSize(12 * 3, 12 * 4))
        outer_layout.addWidget(QLabel('As index :'), 0, 2)
        outer_layout.addWidget(self._idx_list, 1, 2)
        return outer_layout

    def _hdr_UI(self):
        outer_layout = QGridLayout()

        self._hdr_spinbox = QSpinBox()
        # self._idx_spinbox.setFixedWidth(36)
        outer_layout.addWidget(QLabel('Row #'), 0, 0)
        outer_layout.addWidget(self._hdr_spinbox, 1, 0)

        bttn_layout = QVBoxLayout()
        self._hdr_add_btn = QPushButton()
        self._hdr_add_btn.setText('>')
        self._hdr_add_btn.clicked.connect(self.onHdrAddBtnClicked)
        self._hdr_rem_btn = QPushButton()
        self._hdr_rem_btn.setText('<')
        # self._hdr_rem_btn.setFixedWidth(12)
        self._hdr_rem_btn.clicked.connect(self.onHdrRemBtnClicked)
        bttn_layout.addWidget(self._hdr_add_btn)
        bttn_layout.addWidget(self._hdr_rem_btn)
        outer_layout.addLayout(bttn_layout, 1, 1)

        self._hdr_list = QListWidget()
        self._hdr_list.setFixedSize(QSize(12 * 3, 12 * 4))
        outer_layout.addWidget(QLabel('As header :'), 0, 2)
        outer_layout.addWidget(self._hdr_list, 1, 2)
        return outer_layout

    def _options_UI(self) -> QStackedWidget:
        idx_frame = QFrame()
        idx_frame.setFrameShape(QFrame.StyledPanel)
        idx_frame.setLayout(self._idx_UI())

        col_frame = QFrame()
        col_frame.setFrameShape(QFrame.StyledPanel)
        col_frame.setLayout(self._hdr_UI())

        stack = QStackedWidget()
        stack.addWidget(idx_frame)
        stack.addWidget(col_frame)
        return stack

    def initPropertiesWidget(self):
        """Initialize the layout of properties DockWidget"""
        self.propertiesWidget = QWidget()

        # Import frame
        import_frame = QFrame()
        import_frame.setFrameShape(QFrame.StyledPanel)
        import_frame.setLayout(self._file_UI())

        # Options layout
        self._stack = self._options_UI()

        # center the widget
        outer_layout = QVBoxLayout()
        outer_layout.addStretch()
        outer_layout.addWidget(QLabel('File :'))
        outer_layout.addWidget(import_frame)

        layout = QHBoxLayout()
        self._change_axis = QComboBox()
        self._change_axis.addItems(['row', 'column'])
        self._change_axis.currentIndexChanged.connect(self.onAxisChange)
        layout.addWidget(QLabel('Axis options :'))
        layout.addWidget(self._change_axis)
        layout.addStretch()

        outer_layout.addLayout(layout)
        outer_layout.addWidget(self._stack)
        outer_layout.addStretch()
        self.propertiesWidget.setLayout(outer_layout)

    def onAxisChange(self):
        if self._change_axis.currentText() == 'row':
            self._stack.setCurrentIndex(0)
        else:
            self._stack.setCurrentIndex(1)

    def onIdxAddBtnClicked(self):
        # check items in list widget
        value = self._idx_spinbox.value()
        for row in range(self._idx_list.count()):
            if value == int(self._idx_list.item(row).text()):
                return

        # add new item and increment spinbox
        new_item = QListWidgetItem()
        new_item.setText(str(value))
        self._idx_list.addItem(new_item)
        self._idx_list.setCurrentRow(self._idx_list.count() - 1)
        self._idx_spinbox.setValue(value + 1)
        self.forcedEval()

    def onIdxRemBtnClicked(self):
        # remove from list
        row = self._idx_list.currentRow()
        if row != -1:
            value = int(self._idx_list.takeItem(row).text())
            self._idx_spinbox.setValue(value)
            self.forcedEval()

    def onHdrAddBtnClicked(self):
        # check items in list widget
        value = self._hdr_spinbox.value()
        for row in range(self._hdr_list.count()):
            if value == int(self._hdr_list.item(row).text()):
                return

        # add new item and increment spinbox
        new_item = QListWidgetItem()
        new_item.setText(str(value))
        self._hdr_list.addItem(new_item)
        self._hdr_list.setCurrentRow(self._hdr_list.count() - 1)
        self._hdr_spinbox.setValue(value + 1)
        self.forcedEval()

    def onHdrRemBtnClicked(self):
        # remove from list
        row = self._hdr_list.currentRow()
        if row != -1:
            value = int(self._hdr_list.takeItem(row).text())
            self._hdr_spinbox.setValue(value)
            self.forcedEval()

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

    def getNodeSettings(self) -> dict:
        kwargs = dict()
        # Retrieve index_col from properties dock
        kwargs['index_col'] = None
        for row in range(self._idx_list.count()):
            value = int(self._idx_list.item(row).text())
            if kwargs['index_col'] is None:
                kwargs['index_col'] = [int(value)]
            else:
                kwargs['index_col'].append(int(value))

        kwargs['header'] = None
        for row in range(self._hdr_list.count()):
            value = int(self._hdr_list.item(row).text())
            if kwargs['header'] is None:
                kwargs['header'] = [int(value)]
            else:
                kwargs['header'].append(int(value))

        # Retrieve encoding argument
        kwargs['encoding'] = self._combo_encoding.currentText()

        # file_path
        kwargs['filepath_or_buffer'] = self.filepath

        return kwargs

    def restoreNodeSettings(self, data: dict) -> bool:
        kwargs = data['node_settings']
        # restore file_path
        self._path_text.setText(kwargs['filepath_or_buffer'])
        # restore options
        index = self._combo_encoding.findText(kwargs['encoding'], Qt.MatchFixedString)
        if index > 0:
            self._combo_encoding.setCurrentIndex(index)
        if kwargs['index_col']:
            for value in kwargs['index_col']:
                new_item = QListWidgetItem()
                new_item.setText(str(value))
                self._idx_list.addItem(new_item)

        return True

    def evalImplementation(self, force=False):
        self.print('evalImplementation')
        kwargs = self.getNodeSettings()
        print(kwargs)

        if self.filepath != '':
            # store the last modified time of the file
            if not self.file_last_modified:
                self.file_last_modified = os.path.getmtime(self.filepath)

            elif self.file_last_modified == os.path.getmtime(self.filepath) and not force:
                # the file has already been loaded, simply return the values stored
                return self.value

            with open(self.filepath) as f:
                # automatically detect delimiters
                dialect = csv.Sniffer().sniff(f.read(4096), delimiters=';, \t')

            # load csv file
            data_frame = pd.read_csv(dialect=dialect, **kwargs)
            # by default cast some column to numeric type if possible
            data_frame = data_frame.apply(pd.to_numeric, errors='ignore')
            self.value = data_frame

            self.markDirty(False)
            self.markInvalid(False)

            self.markDescendantInvalid(False)
            self.markDescendantDirty()

            self.setToolTip('')

            self.evalChildren()

        return self.value


    # def serialize(self):
    #     # Additionally store the file path
    #     result = super().serialize()
    #     result['node_settings'] = self.getNodeSettings()
    #     return result

    # def deserialize(self, data, hashmap=None, restore_id=True):
    #     """Restore node including the file path"""
    #     if hashmap is None:
    #         hashmap = {}
    #     result = super().deserialize(data, hashmap, restore_id)
    #     # retrieve settings
    #
    #     return result
