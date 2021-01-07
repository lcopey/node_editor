import sys, os
from PyQt5.QtWidgets import QApplication
from node_editor.utils import dumpException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from examples.example_data.data_window import DataWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.screens()[0]
    dpi = screen.physicalDotsPerInch()
    print(dpi)

    app.setStyle('Fusion')
    wnd = DataWindow()
    wnd.show()
    wnd.onFileNew()
    sys.exit(app.exec_())
