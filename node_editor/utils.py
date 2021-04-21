import traceback
import os
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication
from pprint import PrettyPrinter
from typing import Union, List

pp = PrettyPrinter(indent=4).pprint


def dumpException(e):
    traceback.print_exc()


def get_path_relative_to_file(file: str, *args: str) -> str:
    """Return path relative to file provided

    Parameters
    ----------
    file : str
        path to current file
    args : str
        additional path to join on

    Returns
    -------
    str
        path relative to file
    """
    return os.path.join(os.path.dirname(file), *args)


def return_simple_id(obj, text):
    return "<{} {}...{}>".format(text, f'{id(obj):02x}'[2:5], f'{id(obj):02x}'[-3:])


def print_items(item):
    if 'GraphicsEdge' in item.__str__():
        print(item)
        print('EDGE : ', item.edge)
        print('  Start socket : ', item.edge.start_socket)
        print('  End socket : ', item.edge.end_socket)

    elif 'GraphicsSocket' in item.__str__():
        print('SOCKET :', item.socket)
        print('  Edges :', item.socket.edges)

    elif 'GraphicsNode' in item.__str__():
        print('NODE :', item.node)
        print('  Input socket :', *item.node.inputs)
        print('  Output socket :', *item.node.outputs)

    else:
        print(item)


def loadStylessheet(filename):
    """Helper function - Load a single stylesheet in the current application.

    Parameters
    ----------
    filename: str
        path to filename.qss
    Returns
    -------
    None
    """
    print('STYLE loading', filename)
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))


def loadStylessheets(*args):
    """Helper function - Load stylesheets in the current application and merge them.

    Parameters
    ----------
    args : str or list of str
        path to filename.qss
    """
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding='utf-8')
    QApplication.instance().setStyleSheet(res)
