import traceback
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4).pprint


def print_func_name(func):
    def inner(*args, **kwargs):
        print(f'Entering function : {func.__name__}')
        return func(*args, **kwargs)

    return inner


def dumpException(e):
    print('Exception:', e)
    traceback.print_tb(e.__traceback__)


def loadStylessheet(filename):
    print('STYLE loading', filename)
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))


def loadStylessheets(*args):
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding='utf-8')
    QApplication.instance().setStyleSheet(res)
