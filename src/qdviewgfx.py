# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QGraphicsView, QApplication

from qdsocketgfx import QD_SocketGfx
from qdedgegfx import QD_EdgeGfx
from qdedge import QD_Edge, EdgeType
from qdcutline import QD_CutLine
from qdutils import *

MODE_NOOP = 1  #: Mode representing ready state
MODE_NODE_RESIZE = 2 # Mode representing when we resize a node
MODE_EDGE_DRAG = 3  #: Mode representing when we drag edge state
MODE_EDGE_CUT = 4  #: Mode representing when we draw a cutting edge

#: Distance when click on socket to enable `Drag QD_Edge`
EDGE_DRAG_START_THRESHOLD = 50


class QD_ViewGfx(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, gfx: 'QD_SceneGfx', parent: 'QWidget' = None):
        super().__init__(parent)
        self.gfx = gfx

        self.initUI()
        self.setScene(self.gfx)

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
        self.cutline = QD_CutLine()
        self.gfx.addItem(self.cutline)

        # listeners
        self._drag_enter_listeners = []
        self._drop_listeners = []

    def initUI(self):
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        # enable dropping
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        for callback in self._drag_enter_listeners:
            callback(event)

    def dropEvent(self, event: QDropEvent):
        for callback in self._drop_listeners:
            callback(event)

    def addDragEnterListener(self, callback: 'function'):
        self._drag_enter_listeners.append(callback)

    def addDropListener(self, callback: 'function'):
        self._drop_listeners.append(callback)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        item = self.getItemAtClick(event)

        # debug print out
        if confg.DEBUG:
            if isinstance(item, QD_EdgeGfx):
                print("MMB DEBUG:", item.edge, "\n\t", item.edge.gfx if item.edge.gfx is not None else None)

            if isinstance(item, QD_SocketGfx):
                print("MMB DEBUG:", item.socket, "socket_type:", item.socket.socket_type, "has edges:", "no" if item.socket.edges == [] else "")
                if item.socket.edges:
                    for edge in item.socket.edges: print("\t", edge)

        if confg.DEBUG and (item is None):
            print("SCENE:")
            print("  Nodes:")

            for node in self.gfx.scene.nodes:
                print("\t", node)

            print("  Edges:")
            for edge in self.gfx.scene.edges:
                print("\t", edge, "\n\t\tgfxEdge:", edge.gfx if edge.gfx is not None else None)

            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                print("  Graphic Items in GraphicScene:")
                for item in self.gfx.items():
                    print('    ', item)

        # faking events for enable MMB dragging the scene
        releaseEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.position(), event.globalPosition(), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.position(), event.globalPosition(), Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        fakeEvent = QMouseEvent(event.type(), event.position(), event.globalPosition(), Qt.MouseButton.LeftButton, event.buttons() & ~Qt.MouseButton.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def leftMouseButtonPress(self, event: QMouseEvent):

        # get item which we clicked on
        item = self.getItemAtClick(event)

        # we store the position of last LMB click
        self.last_lmb_click_scene_pos = self.mapToScene(event.position().toPoint())

        if confg.DEBUG:
            print("LMB Click on", item, self.debug_modifiers(event))

        # logic
        if hasattr(item, "node") or isinstance(item, QD_EdgeGfx) or item is None:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.Type.MouseButtonPress, event.position(), event.globalPosition(), Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers() | Qt.KeyboardModifier.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        if isinstance(item, QD_SocketGfx):
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res:
                return

        if item is None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.position(), event.globalPosition(), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        item = self.getItemAtClick(event)

        try:
            # logic
            if hasattr(item, "node") or isinstance(item, QD_EdgeGfx) or item is None:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    event.ignore()
                    fakeEvent = QMouseEvent(event.type(), event.position(), event.globalPosition(), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers() | Qt.KeyboardModifier.ControlModifier)
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
                QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
                self.mode = MODE_NOOP
                return

            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False
                current_selected_items = self.gfx.selectedItems()

                if current_selected_items != self.gfx.scene._last_selected_items:
                    if current_selected_items == []:
                        self.gfx.itemsDeselected.emit()
                    else:
                        self.gfx.itemSelected.emit()
                    self.gfx.scene._last_selected_items = current_selected_items

                return

            # otherwise deselect everything
            if item is None:
                self.gfx.itemsDeselected.emit()

        except:
            utils.dumpExcept()

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event: QMouseEvent):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event: QMouseEvent):

        ## cannot be because with dragging RMB we spawn Create New QD_OpNode Context Menu
        ## However, you could use this if you want to cancel with RMB
        # if self.mode == MODE_EDGE_DRAG:
        #     self.cancelDragEdge(event)
        #     return

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        scenepos = self.mapToScene(event.position().toPoint())

        if self.mode == MODE_EDGE_DRAG:
            # according to sentry: 'NoneType' object has no attribute 'gfx'
            if self.drag_edge is not None and self.drag_edge.gfx is not None:
                self.drag_edge.gfx.setDestination(scenepos.x(), scenepos.y())
                self.drag_edge.gfx.update()
            else:
                print(">>> Want to update self.drag_edge gfx, but it's None!!!")

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
            how to solve the problem when QD_OpNode does contain Text/LineEdit and we press `Delete`
            key (also serving to delete `QD_OpNode`)

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
        #     self.gfx.scene.saveToFile("graph.json")
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.gfx.scene.loadFromFile("graph.json")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.gfx.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.gfx.scene.history.redo()
        # elif event.key() == Qt.Key_H:
        #     print("HISTORY:     len(%d)" % len(self.gfx.scene.history.history_stack),
        #           " -- current_step", self.gfx.scene.history.history_current_step)
        #     ix = 0
        #     for item in self.gfx.scene.history.history_stack:
        #         print("#", ix, "--", item['desc'])
        #         ix += 1
        # else:
        super().keyPressEvent(event)

    def cutIntersectingEdges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            # @TODO: we could collect all touched nodes, and notify them once after all edges removed
            # we could cut 3 edges leading to a single nodeeditor this will notify it 3x
            # maybe we could use some Notifier class with methods collect() and dispatch()
            for edge in self.gfx.scene.edges:
                if edge.gfx.intersectsWith(p1, p2):
                    edge.remove()
        self.gfx.scene.history.storeHistory("Delete cutted edges", setModified=True)

    def deleteSelected(self):
        for item in self.gfx.selectedItems():
            if isinstance(item, QD_EdgeGfx):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
        self.gfx.scene.history.storeHistory("Delete selected", setModified=True)

    def debug_modifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.KeyboardModifier.AltModifier: out += "ALT "
        return out

    def getItemAtClick(self, event: QEvent) -> 'QGraphicsItem':
        return self.itemAt(event.position().toPoint())

    def edgeDragStart(self, item: 'QGraphicsItem'):
        try:
            if confg.DEBUG:
                print('View::edgeDragStart ~ Start dragging edge')

            if confg.DEBUG:
                print('View::edgeDragStart ~   assign Start QD_Socket to:', item.socket)

            self.drag_start_socket = item.socket
            self.drag_edge = QD_Edge(self.gfx.scene, item.socket, None, EdgeType.Bezier)

            if confg.DEBUG:
                print('View::edgeDragStart ~   dragEdge:', self.drag_edge)
        except Exception as e:
            utils.dumpExcept(e)

    def edgeDragEnd(self, item: 'QGraphicsItem'):
        self.mode = MODE_NOOP

        if confg.DEBUG:
            print('View::edgeDragEnd ~ End dragging edge')

        self.drag_edge.remove(silent=True)  # don't notify sockets about removing drag_edge
        self.drag_edge = None

        try:
            if isinstance(item, QD_SocketGfx):
                if (item.socket != self.drag_start_socket) and (item.socket.type.is_in == self.drag_start_socket.type.is_out) and (item.socket.type.is_pulse == self.drag_start_socket.type.is_pulse):
                    # if we released dragging on a socket (other then the beginning socket)

                    ## First remove old edges / send notifications
                    for socket in (item.socket, self.drag_start_socket):
                        if not socket.is_multi_edges:
                            if socket.is_input:
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAllEdges(silent=False)

                    ## Create new QD_Edge
                    new_edge = QD_Edge(self.gfx.scene, self.drag_start_socket, item.socket, edge_type=EdgeType.Bezier)
                    if confg.DEBUG:
                        print("View::edgeDragEnd ~  created new edge:", new_edge, "connecting", new_edge.start_socket, "<-->", new_edge.end_socket)

                    ## Send notifications for the new edge
                    for socket in [self.drag_start_socket, item.socket]:
                        # @TODO: Add possibility (ie when an input edge was replaced) to be silent and don't trigger change
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input:
                            socket.node.onInputChanged(socket)

                    self.gfx.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                    return True
        except Exception as e:
            utils.dumpExcept(e)

        if confg.DEBUG:
            print('View::edgeDragEnd ~ everything done.')
        return False

    def distanceBetweenClickAndReleaseIsOff(self, event: QMouseEvent) -> bool:
        new_lmb_release_scene_pos = self.mapToScene(event.position().toPoint())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD * EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x() * dist_scene.x() + dist_scene.y() * dist_scene.y()) > edge_drag_threshold_sq

    def wheelEvent(self, event: QWheelEvent):
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
