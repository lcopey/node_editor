from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QByteArray, QMimeData, QPoint, QDataStream, QIODevice
from PyQt5.QtGui import QDrag
from typing import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .child_items import ValuedItem

LISTBOX_W_VALUE_MIMETYPE = "application/draggedItem"


def _getData(itemData: QByteArray, value: Any):
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


# TODO include in child item class
def _getDragObject(parent: QWidget, item: Union['ValuedItem']) -> QDrag:
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
    _getData(itemData, item.value)

    mimeData = QMimeData()
    mimeData.setData(LISTBOX_W_VALUE_MIMETYPE, itemData)

    drag = QDrag(parent)
    drag.setHotSpot(QPoint(0, 0))
    drag.setMimeData(mimeData)
    return drag


def _getValueFromMime(mime):
    itemData = mime.data(LISTBOX_W_VALUE_MIMETYPE)
    dataStream = QDataStream(itemData, QIODevice.ReadOnly)
    value = dataStream.readQVariantList()
    if len(value) == 1:
        value = value[0]
    else:
        value = tuple(value)
    return value
