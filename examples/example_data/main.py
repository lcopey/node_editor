import sys, os
from PyQt5.QtWidgets import QApplication
from node_editor.utils import dumpException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

#     dll_dir = os.path.dirname(__file__) + '\\..\\..\\..\\Library\\bin' attempt to fix by adding Qt5Core_conda.dll path in __init__.py of PyQT5

from examples.example_data.data_window import DataWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.screens()[0]
    dpi = screen.physicalDotsPerInch()
    print(dpi)
    # dpi 267.54

    app.setStyle('Fusion')
    wnd = DataWindow()
    wnd.show()
    wnd.onFileNew()
    sys.exit(app.exec_())
