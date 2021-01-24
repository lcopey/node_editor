from PyQt5.QtCore import Qt
from enum import Enum


class Handle(Enum):
    TopLeft = 1
    TopMiddle = 2
    TopRight = 3
    MiddleLeft = 4
    MiddleRight = 5
    BottomLeft = 6
    BottomMiddle = 7
    BottomRight = 8


handleCursors = {
    Handle.TopLeft: Qt.SizeFDiagCursor,
    Handle.TopMiddle: Qt.SizeVerCursor,
    Handle.TopRight: Qt.SizeBDiagCursor,
    Handle.MiddleLeft: Qt.SizeHorCursor,
    Handle.MiddleRight: Qt.SizeHorCursor,
    Handle.BottomLeft: Qt.SizeBDiagCursor,
    Handle.BottomMiddle: Qt.SizeVerCursor,
    Handle.BottomRight: Qt.SizeFDiagCursor,
}

handleUpdate = {
    Handle.TopLeft: (True, True, False, False),
    Handle.TopMiddle: (False, True, False, False),
    Handle.TopRight: (False, True, True, False),
    Handle.MiddleLeft: (True, False, False, False),
    Handle.MiddleRight: (False, False, True, False),
    Handle.BottomLeft: (True, False, False, True),
    Handle.BottomMiddle: (False, False, False, True),
    Handle.BottomRight: (False, False, True, True),
}
