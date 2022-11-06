# -*- coding: utf-8 -*-
"""
A module containing `Graphics View` for NodeEditor
"""
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QGraphicsView, QApplication

from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge, EDGE_TYPE_BEZIER
from node_graphics_cutline import QDMCutLine
from qdutils import *

MODE_NOOP = 1  #: Mode representing ready state
MODE_EDGE_DRAG = 2  #: Mode representing when we drag edge state
MODE_EDGE_CUT = 3  #: Mode representing when we draw a cutting edge

#: Distance when click on socket to enable `Drag Edge`
EDGE_DRAG_START_THRESHOLD = 50

DEBUG = True
DEBUG_MMB_SCENE_ITEMS = False


class QDMGraphicsView(QGraphicsView):
    """Class representing NodeEditor's `Graphics View`"""
    #: pyqtSignal emitted when cursor position on the `Scene` has changed
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, gfxScene: 'QDMGraphicsScene', parent: 'QWidget' = None):
        """
        :param gfxScene: reference to the :class:`~nodeeditor.node_graphics_scene.QDMGraphicsScene`
        :type gfxScene: :class:`~nodeeditor.node_graphics_scene.QDMGraphicsScene`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **gfxScene** - reference to the :class:`~nodeeditor.node_graphics_scene.QDMGraphicsScene`
        - **mode** - state of the `Graphics View`
        - **zoomInFactor**- ``float`` - zoom step scaling, default 1.25
        - **zoomClamp** - ``bool`` - do we clamp zooming or is it infinite?
        - **zoom** - current zoom step
        - **zoomStep** - ``int`` - the relative zoom step when zooming in/out
        - **zoomRange** - ``[min, max]``

        """
        super().__init__(parent)
        self.gfxScene = gfxScene

        self.initUI()

        self.setScene(self.gfxScene)

        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.last_scene_mouse_position = QPoint(0, 0)
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        # cutline
        self.cutline = QDMCutLine()
        self.gfxScene.addItem(self.cutline)

        # listeners
        self._drag_enter_listeners = []
        self._drop_listeners = []

    def initUI(self):
        """Set up this ``QGraphicsView``"""
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        # enable dropping
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Trigger our registered `Drag Enter` events
        """
        for callback in self._drag_enter_listeners:
            callback(event)

    def dropEvent(self, event: QDropEvent):
        """Trigger our registered `Drop` events
        """
        for callback in self._drop_listeners:
            callback(event)

    def addDragEnterListener(self, callback: 'function'):
        """Register callback for `Drag Enter` event

        :param callback: callback function
        """
        self._drag_enter_listeners.append(callback)

    def addDropListener(self, callback: 'function'):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self._drop_listeners.append(callback)

    def mousePressEvent(self, event: QMouseEvent):
        """Dispatch Qt's mousePress event to corresponding function below
        """
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Dispatch Qt's mouseRelease event to corresponding function below"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        """When Middle mouse button was pressed
        """
        item = self.getItemAtClick(event)

        # debug print out
        if DEBUG_MMB_SCENE_ITEMS:
            if isinstance(item, QDMGraphicsEdge):
                print("MMB DEBUG:", item.edge, "\n\t", item.edge.gfxEdge if item.edge.gfxEdge is not None else None)

            if isinstance(item, QDMGraphicsSocket):
                print("MMB DEBUG:", item.socket, "socket_type:", item.socket.socket_type, "has edges:", "no" if item.socket.edges == [] else "")
                if item.socket.edges:
                    for edge in item.socket.edges: print("\t", edge)

        if DEBUG_MMB_SCENE_ITEMS and (item is None):
            print("SCENE:")
            print("  Nodes:")

            for node in self.gfxScene.scene.nodes:
                print("\t", node)

            print("  Edges:")
            for edge in self.gfxScene.scene.edges:
                print("\t", edge, "\n\t\tgfxEdge:", edge.gfxEdge if edge.gfxEdge is not None else None)

            if event.modifiers() & Qt.CTRL:
                print("  Graphic Items in GraphicScene:")
                for item in self.gfxScene.items():
                    print('    ', item)

        # faking events for enable MMB dragging the scene
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """When Middle mouse button was released"""
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event: QMouseEvent):
        """When Left  mouse button was pressed"""

        # get item which we clicked on
        item = self.getItemAtClick(event)

        # we store the position of last LMB click
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # if DEBUG: print("LMB Click on", item, self.debug_modifiers(event))

        # logic
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.Type.MouseButtonPress, event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers() | Qt.KeyboardModifier.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        if isinstance(item, QDMGraphicsSocket):
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        if item is None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        """When Left  mouse button was released"""

        # get item which we release mouse button on
        item = self.getItemAtClick(event)

        try:
            # logic
            if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    event.ignore()
                    fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers() | Qt.KeyboardModifier.ControlModifier)
                    super().mouseReleaseEvent(fakeEvent)
                    return

            if self.mode == MODE_EDGE_DRAG:
                if self.distanceBetweenClickAndReleaseIsOff(event):
                    res = self.edgeDragEnd(item)
                    if res: return

            if self.mode == MODE_EDGE_CUT:
                self.cutIntersectingEdges()
                self.cutline.line_points = []
                self.cutline.update()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.mode = MODE_NOOP
                return

            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False
                current_selected_items = self.gfxScene.selectedItems()

                if current_selected_items != self.gfxScene.scene._last_selected_items:
                    if current_selected_items == []:
                        self.gfxScene.itemsDeselected.emit()
                    else:
                        self.gfxScene.itemSelected.emit()
                    self.gfxScene.scene._last_selected_items = current_selected_items

                return

            # otherwise deselect everything
            if item is None:
                self.gfxScene.itemsDeselected.emit()

        except:
            utils.dumpExcept()

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event: QMouseEvent):
        """When Right mouse button was pressed"""
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event: QMouseEvent):
        """When Right mouse button was release"""

        ## cannot be because with dragging RMB we spawn Create New Node Context Menu
        ## However, you could use this if you want to cancel with RMB
        # if self.mode == MODE_EDGE_DRAG:
        #     self.cancelDragEdge(event)
        #     return

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Overriden Qt's ``mouseMoveEvent`` handling Scene/View logic"""
        scenepos = self.mapToScene(event.pos())

        if self.mode == MODE_EDGE_DRAG:
            # according to sentry: 'NoneType' object has no attribute 'gfxEdge'
            if self.drag_edge is not None and self.drag_edge.gfxEdge is not None:
                self.drag_edge.gfxEdge.setDestination(scenepos.x(), scenepos.y())
                self.drag_edge.gfxEdge.update()
            else:
                print(">>> Want to update self.drag_edge gfxEdge, but it's None!!!")

        if self.mode == MODE_EDGE_CUT and self.cutline is not None:
            self.cutline.line_points.append(scenepos)
            self.cutline.update()

        self.last_scene_mouse_position = scenepos

        self.scenePosChanged.emit(int(scenepos.x()), int(scenepos.y()))

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """
        .. note::
            This overriden Qt's method was used for handling key shortcuts, before we implemented propper
            ``QWindow`` with Actions and Menu. Still the commented code serves as an example how to handle
            key presses without Qt's framework for Actions and shortcuts. There can be also found an example
            how to solve the problem when Node does contain Text/LineEdit and we press `Delete`
            key (also serving to delete `Node`)

        :param event: Qt's Key event
        :type event: ``QKeyEvent``
        :return:
        """
        # Use this code below if you wanna have shortcuts in this widget.
        # You want to use this, when you don't have a window which handles these shortcuts for you

        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.gfxScene.scene.saveToFile("graph.json")
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.gfxScene.scene.loadFromFile("graph.json")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.gfxScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.gfxScene.scene.history.redo()
        # elif event.key() == Qt.Key_H:
        #     print("HISTORY:     len(%d)" % len(self.gfxScene.scene.history.history_stack),
        #           " -- current_step", self.gfxScene.scene.history.history_current_step)
        #     ix = 0
        #     for item in self.gfxScene.scene.history.history_stack:
        #         print("#", ix, "--", item['desc'])
        #         ix += 1
        # else:
        super().keyPressEvent(event)

    def cutIntersectingEdges(self):
        """Compare which `Edges` intersect with current `Cut line` and delete them safely"""
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            # @TODO: we could collect all touched nodes, and notify them once after all edges removed
            # we could cut 3 edges leading to a single nodeeditor this will notify it 3x
            # maybe we could use some Notifier class with methods collect() and dispatch()
            for edge in self.gfxScene.scene.edges:
                if edge.gfxEdge.intersectsWith(p1, p2):
                    edge.remove()
        self.gfxScene.scene.history.storeHistory("Delete cutted edges", setModified=True)

    def deleteSelected(self):
        """Shortcut for safe deleting every object selected in the `Scene`."""
        for item in self.gfxScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
        self.gfxScene.scene.history.storeHistory("Delete selected", setModified=True)

    def debug_modifiers(self, event):
        """Helper function get string if we hold Ctrl, Shift or Alt modifier keys"""
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "
        return out

    def getItemAtClick(self, event: QEvent) -> 'QGraphicsItem':
        """Return the object on which we've clicked/release mouse button

        :param event: Qt's mouse or key event
        :type event: ``QEvent``
        :return: ``QGraphicsItem`` which the mouse event happened or ``None``
        """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edgeDragStart(self, item: 'QGraphicsItem'):
        """Code handling the start of dragging an `Edge` operation"""
        try:
            if DEBUG: print('View::edgeDragStart ~ Start dragging edge')
            if DEBUG: print('View::edgeDragStart ~   assign Start Socket to:', item.socket)
            self.drag_start_socket = item.socket
            self.drag_edge = Edge(self.gfxScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
            if DEBUG: print('View::edgeDragStart ~   dragEdge:', self.drag_edge)
        except Exception as e:
            utils.dumpExcept(e)

    def edgeDragEnd(self, item: 'QGraphicsItem'):
        """Code handling the end of dragging an `Edge` operation. In this code return True if skip the
        rest of the mouse event processing

        :param item: Item in the `Graphics Scene` where we ended dragging an `Edge`
        :type item: ``QGraphicsItem``
        """
        self.mode = MODE_NOOP

        if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
        self.drag_edge.remove(silent=True)  # don't notify sockets about removing drag_edge
        self.drag_edge = None

        try:
            if isinstance(item, QDMGraphicsSocket):
                if item.socket != self.drag_start_socket:
                    # if we released dragging on a socket (other then the beginning socket)

                    ## First remove old edges / send notifications
                    for socket in (item.socket, self.drag_start_socket):
                        if not socket.is_multi_edges:
                            if socket.is_input:
                                # print("removing SILENTLY edges from input socket (is_input and !is_multi_edges) [DragStart]:", item.socket.edges)
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAllEdges(silent=False)

                    ## Create new Edge
                    new_edge = Edge(self.gfxScene.scene, self.drag_start_socket, item.socket, edge_type=EDGE_TYPE_BEZIER)
                    if DEBUG:
                        print("View::edgeDragEnd ~  created new edge:", new_edge, "connecting", new_edge.start_socket, "<-->", new_edge.end_socket)

                    ## Send notifications for the new edge
                    for socket in [self.drag_start_socket, item.socket]:
                        # @TODO: Add possibility (ie when an input edge was replaced) to be silent and don't trigger change
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input:
                            socket.node.onInputChanged(socket)

                    self.gfxScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                    return True
        except Exception as e:
            utils.dumpExcept(e)

        if DEBUG:
            print('View::edgeDragEnd ~ everything done.')
        return False

    def distanceBetweenClickAndReleaseIsOff(self, event: QMouseEvent) -> bool:
        """ Measures if we are too far from the last Mouse button click scene position.
        This is used for detection if we release too far after we clicked on a `Socket`

        :param event: Qt's mouse event
        :type event: ``QMouseEvent``
        :return: ``True`` if we released too far from where we clicked before
        """
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD * EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x() * dist_scene.x() + dist_scene.y() * dist_scene.y()) > edge_drag_threshold_sq

    def wheelEvent(self, event: QWheelEvent):
        """overriden Qt's ``wheelEvent``. This handles zooming"""
        # calculate our zoom Factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)
