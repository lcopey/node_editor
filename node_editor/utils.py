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


def return_simple_id(obj, text):
    return "<{} {}...{}>".format(text, f'{id(obj):02x}'[2:5], f'{id(obj):02x}'[-3:])


def print_scene(scene):
    """Affiche les éléments actuels de la scene"""
    print('SCENE')
    print('  Nodes :')
    [print(node) for node in scene.nodes]
    print('  Edges :')
    [print(edge) for edge in scene.edges]


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


def dumpException(e):
    # print('Exception:', e.__class__, e)
    # traceback.print_tb(e.__traceback__)
    traceback.print_exc()


def loadStylessheet(filename):
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
