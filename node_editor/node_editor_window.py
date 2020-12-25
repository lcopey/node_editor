import os
import json
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, QApplication, QMessageBox
from .node_editor_widget import NodeEditorWidget
from PyQt5.QtGui import QCloseEvent

DEBUG = True


class NodeEditorWindow(QMainWindow):
    """Main application window

    Contains :
        - menubar with File, Edit
        - statusbar displaying cursor position on the scene
        - NodeEditorWidget instance containing a graphics view and the scene
    """

    def __init__(self):
        super().__init__()
        self.filename = None
        self.initUI()

    def createAct(self, name: str, shortcut: str, tooltip: str, callback: 'function') -> QAction:
        """Utility function - create action to add in menubar

        Parameters
        ----------
        name : str
            Name to display in the menubar
        shortcut : str
            Keyboard shortcut - Exemple : Ctrl+C
        tooltip : str
            Tooltip to display on hover
        callback : function
            function to call on click

        Returns
        -------
        QAction
            Returns a QAction with defined name, shortcut and tooltip

        """
        act = QAction(name, self)  # create new QAction
        act.setShortcut(shortcut)  # Assign keyboard shortcut
        act.setToolTip(tooltip)  # Assign tooltip
        act.triggered.connect(callback)  # assign event on click
        return act

    def initUI(self):
        """Initialize main window UI setup"""
        menubar = self.menuBar()

        # Add menubar
        # initialize main menu
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.createAct('&New', 'Ctrl+N', 'Create new graph', self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Open', 'Ctrl+O', 'Open file', self.onFileOpen))
        fileMenu.addAction(self.createAct('&Save', 'Ctrl+S', 'Save file', self.onFileSave))
        fileMenu.addAction(self.createAct('Save &as', 'Ctrl+Shift+S', 'Save file as', self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('E&xit', 'Ctrl+Q', 'Exit application', self.close))

        # initialize editmenu
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
        """Handle title change updon modification of the scene"""
        title = 'Node Editor - '
        if self.filename is None:
            title += 'New'
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            title += '*'

        self.setWindowTitle(title)

    def isModified(self):
        return self.centralWidget().scene.has_been_modified

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

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close if no change is detected, else prompt a dialog asking to save."""
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def onScenePosChanged(self, x, y):
        """Update mouse position to status bar"""
        self.status_mouse_pos.setText('Scene Pos: [{}, {}]'.format(x, y))

    def onFileNew(self):
        """Clear the scene after prompting dialod asking to save"""
        if self.maybeSave():
            if DEBUG: print('On File New clicked')
            self.centralWidget().scene.clear()
            self.filename = None  # clear filename (default save) when starting new scene
            self.changeTitle()  # reset the title

    def onFileOpen(self):
        """Open OpenFileDialog"""
        if self.maybeSave():
            if DEBUG: print('On File New open')
            # OpenFile dialog
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
            if fname == '':
                return

            if os.path.isfile(fname):
                self.centralWidget().scene.loadFromFile(fname)  # load scene
                self.filename = fname  # store current filename
                self.changeTitle()  # reset title

    def onFileSave(self) -> bool:
        """Save file without dialog. Overwrite filename.
        Return True if save is not canceled and successful."""
        if DEBUG: print('On File save')
        if self.filename is None:  # if no filename exist, open SaveAs dialog
            return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage('Successfully saved {}'.format(self.filename))
        return True

    def onFileSaveAs(self) -> bool:
        """Open SaveAs dialog. Return True if save is not canceled and successful."""
        if DEBUG: print('OnFileSaveAs')
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')
        if fname == '':
            return False
        self.filename = fname
        self.onFileSave()
        self.changeTitle()
        return True

    def onEditUndo(self):
        """Undo callback"""
        if DEBUG: print('Undo')
        self.centralWidget().scene.history.undo()

    def onEditRedo(self):
        """Redo callback"""
        if DEBUG: print('Redo')
        self.centralWidget().scene.history.redo()

    def onEditDelete(self):
        """Delate callback"""
        if DEBUG: print('Delete')
        self.centralWidget().scene.grScene.views()[0].deleteSelected()

    def onEditCut(self):
        """Cut callback"""
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        if DEBUG: print('Cut :', str_data)
        QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        """Copy callback"""
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        if DEBUG: print('Copy :', str_data)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        """Paste callback"""
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
