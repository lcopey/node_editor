from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from widgets import DraggableListWidget, DraggableTreeWidget, ListItem, TreeItem

if __name__ == '__main__':
    import sys
    import numpy as np

    app = QApplication(sys.argv)
    wdg = QWidget()
    upper = DraggableListWidget()
    for n in range(10):
        upper.addItem(ListItem(value=(n, f'item_{n}')))
    lower = DraggableTreeWidget()
    layout = QVBoxLayout()
    layout.addWidget(upper)
    layout.addWidget(lower)

    wdg.setLayout(layout)
    wdg.show()
    sys.exit(app.exec_())
