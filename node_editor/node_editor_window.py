import os
import json
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, QApplication, QMessageBox
from .node_editor_widget import NodeEditorWidget
from PyQt5.QtGui import QCloseEvent

DEBUG = True


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filename = None
        self.initUI()

    def createAct(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act

    def initUI(self):
        menubar = self.menuBar()

        # initialize main menu
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.createAct('&New', 'Ctrl+N', 'Create new graph', self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Open', 'Ctrl+O', 'Open file', self.onFileOpen))
        fileMenu.addAction(self.createAct('&Save', 'Ctrl+S', 'Save file', self.onFileSave))
        fileMenu.addAction(self.createAct('Save &as', 'Ctrl+Shift+S', 'Save file as', self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('E&xit', 'Ctrl+Q', 'Exit application', self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createAct('&Undo', 'Ctrl+Z', 'Undo last operation', self.onEditUndo))
        editMenu.addAction(self.createAct('&Redo', 'Ctrl+Shift+Z', 'Redo last operation', self.onEditRedo))
        editMenu.addSeparator()
        editMenu.addAction(self.createAct('Cu&t', 'Ctrl+X', 'Cut to clipboard', self.onEditCut))
        editMenu.addAction(self.createAct('&Copy', 'Ctrl+C', 'Copy to clipboard', self.onEditCopy))
        editMenu.addAction(self.createAct('&Paste', 'Ctrl+V', 'Paste from clipboard', self.onEditPaste))
        editMenu.addSeparator()
        editMenu.addAction(self.createAct('&Delete', 'Del', 'Delete selected items', self.onEditDelete))

        # set node editor
        nodeEditor = NodeEditorWidget(self)
        nodeEditor.scene.addHasBeenModifiedListener(self.changeTitle)
        self.setCentralWidget(nodeEditor)

        # intialize status bar
        self.statusBar().showMessage('')
        self.status_mouse_pos = QLabel('')
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)

        # set window properties
        self.setGeometry(200, 200, 800, 600)
        self.changeTitle()
        self.show()

    def changeTitle(self):
        title = 'Node Editor - '
        if self.filename is None:
            title += 'New'
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            title += '*'

        self.setWindowTitle(title)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        return self.centralWidget().scene.has_been_modified

    def maybeSave(self):
        # Logic handling the messageBox asking to save the file when closing the window
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, 'About to close your work ?',
                                  'The document has been modified.\n Do you wand to save your changes ?',
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False
        return True

    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText('Scene Pos: [{}, {}]'.format(x, y))

    def onFileNew(self):
        if self.maybeSave():
            if DEBUG: print('On File New clicked')
            self.centralWidget().scene.clear()
            self.filename = None
            self.changeTitle()

    def onFileOpen(self):
        if self.maybeSave():
            if DEBUG: print('On File New open')
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
            if fname == '':
                return

            if os.path.isfile(fname):
                self.centralWidget().scene.loadFromFile(fname)
                self.filename = fname
                self.changeTitle()

    def onFileSave(self) -> bool:
        if DEBUG: print('On File save')
        if self.filename is None:
            return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage('Successfully saved {}'.format(self.filename))
        return True

    def onFileSaveAs(self) -> bool:
        if DEBUG: print('OnFileSaveAs')
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')
        if fname == '':
            return False
        self.filename = fname
        self.onFileSave()
        self.changeTitle()
        return True

    def onEditUndo(self):
        if DEBUG: print('Undo')
        self.centralWidget().scene.history.undo()

    def onEditRedo(self):
        if DEBUG: print('Redo')
        self.centralWidget().scene.history.redo()

    def onEditDelete(self):
        if DEBUG: print('Delete')
        self.centralWidget().scene.grScene.views()[0].deleteSelected()

    def onEditCut(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        if DEBUG: print('Cut :', str_data)
        QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        if DEBUG: print('Copy :', str_data)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        raw_data = QApplication.instance().clipboard().text()
        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print('Pasting of not valid json data', e)
            return
        # check if json data are correct
        if 'nodes' not in data:
            print('JSON does not contain any nodes')
            return

        self.centralWidget().scene.clipboard.deserializeFromClipboard(data)
