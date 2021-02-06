import sys
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtWidgets import QHeaderView, QStyleOptionButton, QStyle, QApplication, QTableView, QWidget, QVBoxLayout


class CheckBoxHeader(QHeaderView):
    clicked = pyqtSignal(int, bool)