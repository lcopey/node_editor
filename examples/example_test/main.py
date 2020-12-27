import sys
import os
import inspect
from PyQt5.QtWidgets import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from node_editor.node_editor_window import NodeEditorWindow
from node_editor.utils import loadStylessheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = NodeEditorWindow()
    module_path = os.path.dirname(inspect.getfile(wnd.__class__))

    loadStylessheet(os.path.join(module_path, 'qss\\nodestyle.qss'))

    sys.exit(app.exec_())
