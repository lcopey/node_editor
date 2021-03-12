from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import traceback

from typing import Union, List, Any, Iterable

LISTBOX_W_VALUE_MIMETYPE = "application/draggedItem"


def dumpException(e):
    # print('Exception:', e.__class__, e)
    # traceback.print_tb(e.__traceback__)
    traceback.print_exc()


def getData(itemData: QByteArray, value: Any):
    """Construct a QDataStream containing item value as a QVariantList

    Parameters
    ----------
    itemData: QByteArray
    """
    dataStream = QDataStream(itemData, QIODevice.WriteOnly)
    if (type(value) == str) or not hasattr(value, '__iter__'):
        dataStream.writeQVariantList([value])
    else:
        dataStream.writeQVariantList(value)


def getDragObject(parent: QWidget, item: Union['SourceListWidgetItem', 'DestTreeWidgetItem']) -> QDrag:
    """Instantiate QDrag of type application/draggerItem with corresponding QMimeData

    Parameters
    ----------
    parent: QWidget
    item: Union['SourceListWidgetItem', 'DestTreeWidgetItem']

    Returns
    -------
    QDrag
        QDrag object holding item value as QMimeData
    """
    # construct dataStream with item value
    itemData = QByteArray()
    getData(itemData, item.value)

    mimeData = QMimeData()
    mimeData.setData(LISTBOX_W_VALUE_MIMETYPE, itemData)

    drag = QDrag(parent)
    drag.setHotSpot(QPoint(0, 0))
    drag.setMimeData(mimeData)
    return drag


def getValueFromMime(mime):
    itemData = mime.data(LISTBOX_W_VALUE_MIMETYPE)
    dataStream = QDataStream(itemData, QIODevice.ReadOnly)
    value = dataStream.readQVariantList()
    if len(value) == 1:
        value = value[0]
    else:
        value = tuple(value)
    return value
