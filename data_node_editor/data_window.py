# -*- encoding: utf-8 -*-
"""
Module implementing the MainWindow to the calculator example
"""
from .data_subwindow import DataSubWindow
from .data_node_base import Configurable
from .data_drag_listbox import DragListBox
from .data_conf import NodeFactory
# Import to include the node in the toolbar
from .nodes import *

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QSignalMapper, Qt

from node_editor.utils import loadStylessheets
from node_editor.node_editor_window import NodeEditorWindow
from node_editor.node_editor_widget import NodeEditorWidget
from node_editor.utils import dumpException, pp, get_path_relative_to_file

from node_editor.node_edge import Edge
from node_editor.node_edge_validators import *

from typing import Optional, Union, Tuple, Callable

# Edge.registerEdgeValidator(edge_validator_debug)
Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)

DEBUG = True


class DataWindow(NodeEditorWindow):
    """Class representing the MainWindow of the application.

    It implements multiple documents area as well as two docks on the left and right.
    The left one displays a list of nodes.
    The right one displays parameters for some nodes.

    **Instance Attributes**
        name_company and name_product - used to register the settings
        mdiArea - Multiple Document Area holding the NodeEditor Widget
    """

    def __init__(self):
        # Instantiates attributes
        # styles attributes
        self._empty_icon: Optional[QIcon] = None  # icon used for subwindow
        self._stylesheet_filenames: Optional[Tuple] = None
        # mdiArea attributes
        self._windowMapper: Optional[QSignalMapper] = None
        self.mdiArea: Optional[QMdiArea] = None
        # Bar menu
        self.windowMenu: Optional[QMenuBar] = None
        self.helpMenu: Optional[QMenuBar] = None
        #  Action from windowMenu
        self.actClose: Optional[QAction] = None
        self.actCloseAll: Optional[QAction] = None
        self.actTile: Optional[QAction] = None
        self.actCascade: Optional[QAction] = None
        self.actNext: Optional[QAction] = None
        self.actPrevious: Optional[QAction] = None
        self.actSeparator: Optional[QAction] = None
        self.actAbout: Optional[QAction] = None
        # Dock holding the properties
        self.propDock: Optional[QDockWidget] = None
        self.propDockLbl: Optional[QLabel] = None
        # Dock holding the nodes list
        self.nodesDock: Optional[QDockWidget] = None
        self.nodeListWidget: Optional[DragListBox] = None

        super(DataWindow, self).__init__()

    def initUI(self):
        """UI is composed of two docks :
        - the one on the left is used to display nodes available to use.
        - the one on the right displays properties of the selected node."""

        # variable for QSettings
        self.name_company = 'Copey'
        self.name_product = 'DataViz NodeEditor'
        main_icon_path = get_path_relative_to_file(__file__, 'resources/main-icon.png')
        self.setWindowIcon(QIcon(main_icon_path))

        # Load filesheets
        # TODO Review style
        # self._stylesheet_filenames = (os.path.join(os.path.dirname(__file__), 'qss/nodeeditor.qss'),
        #                              os.path.join(os.path.dirname(__file__), 'qss/nodeeditor-dark.qss'))
        self._stylesheet_filenames = (get_path_relative_to_file(__file__, 'resources/nodeeditor.qss'))
        self.print(self._stylesheet_filenames)
        loadStylessheets(*self._stylesheet_filenames)
        # self._empty_icon = QIcon("../examples/example_data")
        self._empty_icon = QIcon("../")

        if DEBUG:
            self.print('Registered Node')
            pp(NodeFactory.get_nodes())

        # Instantiate the MultiDocument Area as the CentralWidget
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setTabsClosable(True)
        self.setCentralWidget(self.mdiArea)

        # Connect subWindowActivate to updateMenu
        # Activate the items on the file_menu and the edit_menu
        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.mdiArea.subWindowActivated.connect(self.refreshPropertiesDock)

        # from mdi example...
        self._windowMapper = QSignalMapper(self)
        self._windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        # instantiate various elements
        self.createNodesDock()
        self.createPropertiesDock()
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("DataViz NodeEditor")

    def _createAction(self, label: str, statusTip: str, triggered: Callable, shortcut=None):
        """Create a new QAction to populate the main tool.

        Parameters
        ----------
        label: str
            label of the action
        statusTip: str
            Tooltip
        triggered: Callable
            Callback to trigger when clicking the action
        shortcut: Optional[QKeySequence]
            Key sequence as shortcut for the action

        Returns
        -------
        QAction

        """
        kwargs = {'statusTip': statusTip, 'triggered': triggered}
        if shortcut:
            kwargs['shortcut'] = shortcut
        return QAction(label, self, **kwargs)

    def createActions(self):
        """Instantiate various `QAction` for the main toolbar.

        File and Edit menu actions are instantiated in the :classs:~`node_editor.node_editor_widget.NodeEditorWidget`
        Window and Help actions are specific to the :class:~`examples.calc_window.CalcWindow`
        """
        super().createActions()
        self.actClose = self._createAction("Cl&ose", statusTip="Close the active window",
                                           triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = self._createAction("Close &All", statusTip="Close all the windows",
                                              triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = self._createAction("&Tile", statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = self._createAction("&Cascade", statusTip="Cascade the windows",
                                             triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = self._createAction("Ne&xt", shortcut=QKeySequence.NextChild,
                                          statusTip="Move the focus to the next window",
                                          triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = self._createAction("Pre&vious", shortcut=QKeySequence.PreviousChild,
                                              statusTip="Move the focus to the previous window",
                                              triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = self._createAction("&About", statusTip="Show the application's About box", triggered=self.about)

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

    def createToolBars(self):
        pass

    def createPropertiesDock(self):
        self.propDock = QDockWidget('Properties')
        self.propDock.setFloating(False)
        self.propDock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        propDockLayout = QVBoxLayout()
        self.propDockLbl = QLabel('')
        self.propDockLbl.setWordWrap(True)
        self.propDockLbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # layout of node properties will be set to _propDockWdg
        propDockWdg = QWidget()
        self.propDock.setWidget(propDockWdg)
        propDockWdg.setLayout(propDockLayout)
        self.addDockWidget(Qt.RightDockWidgetArea, self.propDock)

    def createNodesDock(self):
        """Create `Nodes Dock` and populates it with the list of `Nodes`

        The `Nodes` are automatically detected via the :class:~`examples.calc_drag_listbox.QNEDragListBox`
        """
        # populates the nodes dock with automatically discovered nodes in DragListBox
        self.nodeListWidget = DragListBox()

        self.nodesDock = QDockWidget("nodes")
        self.nodesDock.setWidget(self.nodeListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesDock)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready", )

    def onFileNew(self):
        """Create a new mdi Child"""
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
        except Exception as e:
            dumpException(e)

    def onFileOpen(self):
        """Open OpenFileDialog"""
        # OpenFile dialog
        fnames, file_filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(),
                                                           self.getFileDialogFilter())

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # Do not use createMdiChild as a new node editor to call the fileLoad method
                        # Create new subwindow and open file
                        nodeeditor = DataSubWindow()
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage(f'File {fname} loaded', 5000)
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()
        except Exception as e:
            dumpException(e)

    def onSubWndClose(self, widget: DataSubWindow, event: QCloseEvent):
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

    def onWindowNodesToolbar(self):
        """Event handling the visibility of the `Nodes Dock`"""
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def onPropertiesNodesToolbar(self):
        """Event handling the visibility of the `Nodes Dock`"""
        if self.propDock.isVisible():
            self.propDock.hide()
        else:
            self.propDock.show()

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
        """Gray the properties of the editMenu in function of the active subwindow
        """
        self.print('updateEditMenu')
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
        """Gray the properties of the editMenu in function of the active subwindow"""
        # clear all actions in window menu
        self.windowMenu.clear()

        # Add nodes toolbar action to window menu
        toolbar_nodes = self.windowMenu.addAction('Nodes toolbar')
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())

        # Fill all other actions of window menu
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

        # Add properties toolbar action to window menu
        toolbar_properties = self.windowMenu.addAction('Properties toolbar')
        toolbar_properties.setCheckable(True)
        toolbar_properties.triggered.connect(self.onPropertiesNodesToolbar)
        toolbar_properties.setChecked(self.propDock.isVisible())

        # Add windows actions to window menu
        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            wnd_nb = f'{i + 1}' if i >= 9 else f'&{i + 1}'
            text = wnd_nb + f'{child.getUserFriendlyFilename()}'

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self._windowMapper.map)
            self._windowMapper.setMapping(action, window)

    def getCurrentNodeEditorWidget(self) -> Optional[Union[NodeEditorWidget, QWidget]]:
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

    def createMdiChild(self, child_widget: Optional[DataSubWindow] = None) -> QMdiSubWindow:
        """Add a new widget to mdiArea.

        Parameters
        ----------
        child_widget: Optional[DataSubWindow]
            if provided add DataSubWindow to mdiArea else instantiate a new one

        Returns
        -------
        QMdiSubWindow

        """
        datasubwnd = child_widget if child_widget is not None else DataSubWindow()
        subwnd = self.mdiArea.addSubWindow(datasubwnd, )
        subwnd.setWindowIcon(self._empty_icon)

        # update the Edit menu and the dock properties at each time stamp (modifying the scene)
        datasubwnd.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        datasubwnd.scene.history.addHistoryModifiedListener(self.refreshPropertiesDock)
        datasubwnd.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def findMdiChild(self, filename: str) -> Optional[QMdiSubWindow]:
        """Retrieve subwindow according to filename

        Parameters
        ----------
        filename: str
            name of the subwindow

        Returns
        -------
        Optional[QMdiSubWindow]

        """
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None

    def setActiveSubWindow(self, window: QMdiSubWindow):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def refreshPropertiesDock(self):
        # TODO separate the toolbar with one bottom widget holding
        #  some informations and a upper part holding a layout specific to each node
        self.print('Dock properties')
        # get DataSubWindow
        if hasattr(self.mdiArea.activeSubWindow(), 'widget'):
            actSubWnd = self.mdiArea.activeSubWindow().widget()
            try:
                # reset layout
                itemsSelected = actSubWnd.scene.getSelectedItems()
                if len(itemsSelected) > 1:
                    self.propDock.setWidget(self.propDockLbl)
                    self.propDockLbl.setText('{} items selected'.format(len(itemsSelected)))

                elif len(itemsSelected) == 1:
                    itemSelected = itemsSelected[0]
                    if hasattr(itemSelected, 'node') and isinstance(itemSelected.node, Configurable):
                        self.propDock.setWidget(itemSelected.node.propertiesWidget)

                    else:
                        self.propDockLbl.setText('{} items selected'.format(len(itemsSelected)))
                        self.propDock.setWidget(self.propDockLbl)

                else:
                    self.propDock.setWidget(self.propDockLbl)
                    self.propDockLbl.setText('No selection')

            except Exception as e:
                dumpException(e)

    def about(self):
        QMessageBox.about(self, "About Calculator NodeEditor Example",
                          "The <b>Calculator NodeEditor</b> example demonstrates how to write multiple "
                          "document interface applications using PyQt5 and NodeEditor.")

    def print(self, *args):
        if DEBUG:
            print(f'> {self.__class__.__name__}', *args)

    def __str__(self):
        return 'Main Window'
