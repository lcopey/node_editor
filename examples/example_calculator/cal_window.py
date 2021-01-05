# -*- encoding: utf-8 -*-
"""
Module implementing the MainWindow to the calculator example
"""
import os
from PyQt5.QtWidgets import QMdiArea, QWidget, QListWidget, QDockWidget, QAction, QMessageBox, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import QSignalMapper, Qt, QFileInfo
from node_editor.utils import loadStylessheets
from node_editor.node_editor_window import NodeEditorWindow
from node_editor.node_editor_widget import NodeEditorWidget
from node_editor.utils import dumpException, pp
from .calc_sub_window import CalculatorSubWindow
from .calc_drag_listbox import QNEDragListbox
from .calc_conf import CALC_NODES

from node_editor.node_edge import Edge
from node_editor.node_edge_validators import *

Edge.registerEdgeValidator(edge_validator_debug)
Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)
# images for the dark skin
import examples.example_calculator.qss.nodeeditor_dark_resources

DEBUG = False


class CalculatorWindow(NodeEditorWindow):
    """Class representing the MainWindow of the application.

    Instance Attributes:
        name_company and name_product - used to register the settings
    """

    def initUI(self):
        """UI is composed with """

        # variable for QSettings
        self.name_company = 'Michelin'
        self.name_product = 'Calculator NodeEditor'

        # Load filesheets
        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), 'qss/nodeeditor.qss')
        loadStylessheets(os.path.join(os.path.dirname(__file__), 'qss/nodeeditor-dark.qss'),
                         self.stylesheet_filename)

        self.empty_icon = QIcon(".")

        if DEBUG:
            print('Registered Node')
            pp(CALC_NODES)

        # Instantiate the MultiDocument Area
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setTabsClosable(True)
        self.setCentralWidget(self.mdiArea)

        # Connect subWindowActivate to updateMenu
        # Activate the items on the file_menu and the edit_menu
        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        # from mdi example...
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        # instantiate various elements
        self.createNodesDock()
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("Calculator NodeEditor Example")

    def createActions(self):
        """Instantiate various `QAction` for the main toolbar.

        File and Edit menu actions are instantiated in the :classs:~`node_editor.node_editor_widget.NodeEditorWidget`
        Window and Help actions are specific to the :class:~`examples.calc_window.CalcWindow`
        """
        super().createActions()
        self.actClose = QAction("Cl&ose", self, statusTip="Close the active window",
                                triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QAction("Close &All", self, statusTip="Close all the windows",
                                   triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows",
                                  triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild,
                               statusTip="Move the focus to the next window",
                               triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild,
                                   statusTip="Move the focus to the previous window",
                                   triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

    def createMenus(self):
        """Populate File, Edit, Window and Help with `QAction`"""
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)

        # Any time the edit menu is about to be shown, update it
        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def onWindowNodesToolbar(self):
        """Event handling the visibility of the `Nodes Dock`"""
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def createToolBars(self):
        pass

    def createNodesDock(self):
        """Create `Nodes Dock` and populates it with the list of `Nodes`

        The `Nodes` are automatically detected via the :class:~`examples.calc_drag_listbox.QNEDragListBox`
        """
        self.nodeListWidget = QNEDragListbox()

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodeListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready", )

    def updateMenus(self):
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setVisible(hasMdiChild)

        self.updateEditMenu()

    def updateEditMenu(self):
        if DEBUG: print('updateEditMenu')
        try:
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)
            hasSelectedItems = hasMdiChild and active.hasSelectedItems()

            self.actPaste.setEnabled(hasMdiChild)

            self.actCut.setEnabled(hasSelectedItems)
            self.actCopy.setEnabled(hasSelectedItems)
            self.actDelete.setEnabled(hasSelectedItems)

            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e:
            dumpException(e)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction('Nodes toolbar')
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())
        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def getCurrentNodeEditorWidget(self) -> NodeEditorWidget:
        """Return the widget currently holding the scene.

        For different application, the method can be overridden to return mdiArea, the central widget...

        Returns
        -------
        NodeEditorWidget
            Node editor Widget. The widget holding the scene.
        """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def onFileNew(self):
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
        except Exception as e:
            dumpException(e)

    def onFileOpen(self):
        """Open OpenFileDialog"""
        # OpenFile dialog
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(),
                                                      self.getFileDialogFilter())

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # do not use createMdiChild as a new node editor to call the fileLoad method
                        # Create new subwindow and open file
                        nodeeditor = CalculatorSubWindow()
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage(f'File {fname} loaded', 5000)
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()
        except Exception as e:
            dumpException(e)

    def about(self):
        QMessageBox.about(self, "About Calculator NodeEditor Example",
                          "The <b>Calculator NodeEditor</b> example demonstrates how to write multiple "
                          "document interface applications using PyQt5 and NodeEditor.")

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            self.mdiArea.closeAllSubWindows()
            if self.mdiArea.currentSubWindow():
                event.ignore()
            else:
                self.writeSettings()
                event.accept()
                # In case of fixing the application closing
                # import sys
                # sys.exit(0)
        except Exception as e:
            dumpException(e)

    def createMdiChild(self, child_widget=None):
        nodeeditor = child_widget if child_widget is not None else CalculatorSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor, )
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        # nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def onSubWndClose(self, widget: CalculatorSubWindow, event: QCloseEvent):
        # close event from the nodeeditor works by asking the active widget
        # if modification occurs on the active widget, ask to save or not.
        # Therefore when closing a subwindow, select the corresponding subwindow
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        # Does the active widget need to be saved ?
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiChild(self, fileName):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == fileName:
                return window
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)
