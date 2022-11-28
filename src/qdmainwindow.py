# -*- coding: utf-8 -*-
import os
import json
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *
from qdstatewidget import QD_StateWidget
from qdquestwidget import QD_QuestWidget
from qddraglistbox import QD_DragListBox
from qdluaeditor import QD_LuaEditor
from qdutils import *

# images for the dark skin
import qss.nodeeditor_dark_resources

class QD_MainWindow(QMainWindow):
    StateWidget_class = QD_StateWidget


    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/nodeeditor.qss")
        utils.loadStylesheets(os.path.join(os.path.dirname(__file__), "qss/nodeeditor-dark.qss"), self.stylesheet_filename)

        self.empty_icon = QIcon(".")
        utils.printObj(utils.valid_node_types())

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        # self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("Calculator NodeEditor Example")


    def isModified(self) -> bool:
        """Has current :class:`scene.QD_StateScene` been modified?

        :return: ``True`` if current :class:`scene.QD_StateScene` has been modified
        :rtype: ``bool``
        """
        return self.getCurrentStateNodeWidget().scene.isModified()


    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            # hacky fix for PyQt 5.14.x
            import sys
            sys.exit(0)


    def setTitle(self):
        """Function responsible for setting window title
        """
        self.setWindowTitle("QD_Node Editor - " + self.getCurrentStateNodeWidget().getUserFriendlyFilename())


    def createActions(self):
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip="Save file", triggered=self.onFileSave)
        self.actSaveAs = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip="Save file as...", triggered=self.onFileSaveAs)
        self.actExit = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip="Exit application", triggered=self.close)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip="Undo last operation", triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip="Redo last operation", triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip="Cut to clipboard", triggered=self.onEditCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip="Copy to clipboard", triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip="Paste from clipboard", triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip="Delete selected items", triggered=self.onEditDelete)
        self.actLuaEditor = QAction('&LuaEditor', self, shortcut='Ctrl+L', statusTip="Edit lua code", triggered=self.onEditLuaEditor)

        self.actOpenNodeEditWindow = QAction("Open QD_Node Edit Window", self, statusTip="Open node edit window", triggered=self.onOpenNodeEditWindow)

        self.actClose = QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.StandardKey.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QAction("Pre&vious", self, shortcut=QKeySequence.StandardKey.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

    def getCurrentStateNodeWidget(self):
        """ we're returning QD_StateWidget here... """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def onFileNew(self):
        try:
            subwin = self.createMdiChild()
            subwin.widget().fileNew()
            subwin.show()
        except Exception as e:
            utils.dumpExcept(e)

    def onEditLuaEditor(self):
        try:
            subwin = self.createLuaEditorChild()
            subwin.show()
        except Exception as e:
            utils.dumpExcept(e)

    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())
        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # we need to create new subWindow and open the file
                        statesubwin = QD_QuestWidget()
                        if statesubwin.fileLoad(fname):
                            self.statusBar().showMessage("File %s loaded" % fname, 5000)
                            statesubwin.setTitle()
                            subwin = self.createMdiChild(statesubwin)
                            subwin.show()
                        else:
                            statesubwin.close()
        except Exception as e:
            utils.dumpExcept(e)

    def onOpenNodeEditWindow(self):
        print(123)

    def about(self):
        QMessageBox.about(self, "About QuestDesigner",
                          "The <b>QuestDesigner</b> helps to design quests for mir2x game. For more information visit: "
                          "<a href='https://github.com/etorth/mir2x'>github.com/etorth/mir2x</a>")

    def createFileMenu(self):
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)


    def createMenus(self):
        self.createFileMenu()
        self.createEditMenu()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)

        self.editMenu.aboutToShow.connect(self.updateEditMenu)


    def createEditMenu(self):
        menubar = self.menuBar()
        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)
        self.editMenu.addAction(self.actLuaEditor)

    def updateMenus(self):
        # print("update Menus")
        active = self.getCurrentStateNodeWidget()
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
        try:
            # print("update Edit Menu")
            active = self.getCurrentStateNodeWidget()
            hasMdiChild = (active is not None)

            # if not issubclass(type(active), QD_LuaEditor):
            #     self.actPaste.setEnabled(hasMdiChild)
            #
            #     self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            #     self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            #     self.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())
            #
            #     self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            #     self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e:
            utils.dumpExcept(e)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        self.windowMenu.addAction(self.actOpenNodeEditWindow)
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
            action.setChecked(child is self.getCurrentStateNodeWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def createToolBars(self):
        pass


    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
        self.status_mouse_pos = QLabel()
        self.statusBar().addPermanentWidget(self.status_mouse_pos)

    def createMdiChild(self, child_widget=None):
        if child_widget is None:
            child_widget = QD_QuestWidget()

        subwin = self.mdiArea.addSubWindow(child_widget)
        subwin.setWindowIcon(self.empty_icon)

        # child_widget.scene.addItemSelectedListener(self.updateEditMenu)
        # child_widget.scene.addItemsDeselectedListener(self.updateEditMenu)
        child_widget.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        child_widget.addCloseEventListener(self.onSubWndClose)
        child_widget.view.scenePosChanged.connect(self.onScenePosChanged)
        return subwin

    def createLuaEditorChild(self):
        luaeditor = QD_LuaEditor()
        subwin = self.mdiArea.addSubWindow(luaeditor)
        subwin.setWindowIcon(self.empty_icon)
        return subwin


    def onScenePosChanged(self, x: int, y: int):
        """Handle event when cursor position changed on the `QD_StateScene`

        :param x: new cursor x position
        :type x:
        :param y: new cursor y position
        :type y:
        """
        self.status_mouse_pos.setText("LOC: [%d, %d]" % (x, y))



    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None


    def findMdiChildByStateNode(self, state_node):
        for win in self.mdiArea.subWindowList():
            widget = win.widget()
            if isinstance(widget, QD_StateWidget) and widget.node == state_node:
                return win
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)


    def maybeSave(self) -> bool:
        """If current `QD_StateScene` is modified, ask a dialog to save the changes. Used before
        closing window / mdi child document

        :return: ``True`` if we can continue in the `Close Event` and shutdown. ``False`` if we should cancel
        :rtype: ``bool``
        """
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "About to loose your work?", "The document has been modified.\n Do you want to save your changes?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)

        if res == QMessageBox.StandardButton.Save:
            return self.onFileSave()
        elif res == QMessageBox.StandardButton.Cancel:
            return False

        return True


    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''


    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'


    def onFileSave(self):
        """Handle File Save operation"""
        current_nodeeditor = self.getCurrentStateNodeWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet():
                return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage("Successfully saved %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()
            return True


    def onFileSaveAs(self):
        """Handle File Save As operation"""
        current_nodeeditor = self.getCurrentStateNodeWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.getFileDialogDirectory(), self.getFileDialogFilter())
            if fname == '':
                return False

            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage("Successfully saved as %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()
            return True


    def onEditUndo(self):
        """Handle Edit Undo operation"""
        if self.getCurrentStateNodeWidget():
            self.getCurrentStateNodeWidget().scene.history.undo()

    def onEditRedo(self):
        """Handle Edit Redo operation"""
        if self.getCurrentStateNodeWidget():
            self.getCurrentStateNodeWidget().scene.history.redo()

    def onEditDelete(self):
        """Handle Delete Selected operation"""
        if self.getCurrentStateNodeWidget():
            self.getCurrentStateNodeWidget().scene.getView().deleteSelected()


    def onEditCut(self):
        """Handle Edit Cut to clipboard operation"""
        if self.getCurrentStateNodeWidget():
            data = self.getCurrentStateNodeWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)


    def onEditCopy(self):
        """Handle Edit Copy to clipboard operation"""
        if self.getCurrentStateNodeWidget():
            data = self.getCurrentStateNodeWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        """Handle Edit Paste from clipboard operation"""
        if self.getCurrentStateNodeWidget():
            raw_data = QApplication.instance().clipboard().text()

            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print("Pasting of not valid json data!", e)
                return

            # check if the json data are correct
            if 'nodes' not in data:
                print("JSON does not contain any nodes!")
                return

            return self.getCurrentStateNodeWidget().scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self):
        """Read the permanent profile settings for this app"""
        settings = QSettings()
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        """Write the permanent profile settings for this app"""
        settings = QSettings()
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
