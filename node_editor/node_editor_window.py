# -*- encoding: utf-8 -*-
"""Main application window

Contains :
    - menubar with File, Edit
    - statusbar displaying cursor position on the scene
    - NodeEditorWidget instance containing a graphics view and the scene
"""
import os
import json
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, QApplication, QMessageBox
from PyQt5.QtCore import QSettings, QPoint, QSize
from PyQt5.QtGui import QCloseEvent
from .node_editor_widget import NodeEditorWidget
from .utils import dumpException

DEBUG = False


class NodeEditorWindow(QMainWindow):
    NodeEditorWidget_class = NodeEditorWidget  # Static variable to subclass the NodeEditorWidget

    """Class representing NodeEditor's Main Window"""

    def __init__(self):
        super().__init__()
        self.name_company = 'Copey'
        self.name_product = 'NodeEditor'
        self.initUI()

    def initUI(self):
        """Initialize main window UI setup"""
        self.createActions()  # Create actions from the main menubar
        self.createMenus()  # Populate menubar with previous actions

        # set node editor
        self.nodeEditor = self.__class__.NodeEditorWidget_class(self)
        self.nodeEditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeEditor)

        # create status bar
        self.createStatusBar()

        # set window properties
        # self.setGeometry(200, 200, 800, 600)
        self.setTitle()
        self.show()

    def sizeHint(self):
        return QSize(800, 600)

    # noinspection PyArgumentList
    def createActions(self):
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip='Create new graph',
                              triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip='Open file',
                               triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip='Save file',
                               triggered=self.onFileSave)
        self.actSaveAs = QAction('Save &as', self, shortcut='Ctrl+Shift+S', statusTip='Save file as',
                                 triggered=self.onFileSaveAs)
        self.actExit = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip='Exit application',
                               triggered=self.close)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip='Undo last operation',
                               triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip='Redo last operation',
                               triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip='Cut to clipboard',
                              triggered=self.onEditCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip='Copy to clipboard',
                               triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip='Paste from clipboard',
                                triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip='Delete selected items',
                                 triggered=self.onEditDelete)

    def createMenus(self):
        """Utility function, instanciate actions from the menubar"""
        self.createFileMenu()
        self.createEditMenu()

    def createFileMenu(self):
        menubar = self.menuBar()
        # initialize main menu
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

    def createEditMenu(self):
        menubar = self.menuBar()
        # initialize editmenu
        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)

    def createStatusBar(self):
        """Utility function, instantiate the status bar notifying the cursor position in the scene"""
        # intialize status bar
        self.statusBar().showMessage('')
        self.status_mouse_pos = QLabel('')
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        # connect the scene pos changed to a function formatting self.status_mouse_pos
        self.nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)

    def setTitle(self):
        """Handle title change updon modification of the scene"""
        title = 'Node Editor - '
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)

    def isModified(self):
        nodeeditor = self.getCurrentNodeEditorWidget()
        return nodeeditor.scene.isModified() if nodeeditor else False

    def getCurrentNodeEditorWidget(self) -> NodeEditorWidget:
        """Return the widget currently holding the scene.

        For different application, the method can be overridden to return mdiArea, the central widget...

        Returns
        -------
        NodeEditorWidget
            Node editor Widget. The widget holding the scene.
        """
        return self.centralWidget()

    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'

    def maybeSave(self):
        """Handling the dialog asking to save the file when closing the window

        Returns
        -------
        bool
            - True : if change are saved or discarded
            - False : if change are canceled
        """
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
        """Update mouse position to status bar"""
        self.status_mouse_pos.setText('Scene Pos: [{}, {}]'.format(x, y))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close if no change is detected, else prompt a dialog asking to save."""
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def onFileNew(self):
        """Clear the scene after prompting dialod asking to save"""
        if self.maybeSave():
            if DEBUG: print('On File New clicked')
            self.getCurrentNodeEditorWidget().fileNew()
            # self.getCurrentNodeEditorWidget().scene.clear()
            # self.getCurrentNodeEditorWidget().filename = None  # clear filename (default save) when starting new scene
            self.setTitle()  # reset the title

    def onFileOpen(self):
        """Open OpenFileDialog"""
        if self.maybeSave():
            if DEBUG: print('On File New open')
            # OpenFile dialog
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file', self.getFileDialogDirectory(),
                                                        self.getFileDialogFilter())
            if fname == '':
                return

            if os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)
                self.setTitle()

    def onFileSave(self) -> bool:
        """Save file without dialog. Overwrite filename.
        Return True if save is not canceled and successful."""
        if DEBUG: print('On File save')
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet():  # if no filename exist, open SaveAs dialog
                return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage('Successfully saved {}'.format(current_nodeeditor.filename), 5000)

            # support for mdi application, setTitle is contained in the widget instead of the window
            if hasattr(current_nodeeditor, 'setTitle'):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()

            return True

    def onFileSaveAs(self) -> bool:
        """Open SaveAs dialog. Return True if save is not canceled and successful."""
        if DEBUG: print('OnFileSaveAs')
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.getFileDialogDirectory(),
                                                        self.getFileDialogFilter())
            if fname == '':
                return False

            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage('Successfully saved as {}'.format(current_nodeeditor.filename), 5000)

            # support for mdi application, setTitle is contained in the widget instead of the window
            if hasattr(current_nodeeditor, 'setTitle'):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()
            return True

    def onEditUndo(self):
        """Undo callback"""
        if DEBUG: print('Undo')
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor:
            current_nodeeditor.scene.history.undo()

    def onEditRedo(self):
        """Redo callback"""
        if DEBUG: print('Redo')
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor:
            current_nodeeditor.scene.history.redo()

    def onEditDelete(self):
        """Delate callback"""
        if DEBUG: print('Delete')
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor:
            current_nodeeditor.scene.getView().deleteSelected()

    def onEditCut(self):
        """Cut callback"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor:
            data = current_nodeeditor.scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            if DEBUG: print('Cut :', str_data)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        """Copy callback"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor:
            try:
                data = current_nodeeditor.scene.clipboard.serializeSelected(delete=False)

                str_data = json.dumps(data, indent=4)
                if DEBUG: print('Copy :', str_data)
                QApplication.instance().clipboard().setText(str_data)

            except Exception as e:
                dumpException(e)

    def onEditPaste(self):
        """Paste callback"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor:
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

            return current_nodeeditor.scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, self.name_company, self.name_product)
        self.print(settings.fileName())
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
