# -*- coding: utf-8 -*-
import os
import json
from qdutils import *
from qdserializable import QD_Serializable
from qdquestscenegfx import QD_QuestSceneGfx
from qdopnode import QD_OpNode
from qdedge import QD_Edge
from qdscenehistory import QD_SceneHistory
from qdsceneclipboard import QD_SceneClipboard

from qdscenegfx import QD_SceneGfx

class QD_Scene(QD_Serializable):
    SceneGfx_class = QD_SceneGfx

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width = 64000
        self.scene_height = 64000

        # custom flag used to suppress triggering onItemSelected which does a bunch of stuff
        self._silent_selection_events = False

        self._has_been_modified = False
        self._last_selected_items = []

        # initialiaze all listeners
        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        # here we can store callback for retrieving the class for Nodes
        self.node_class_selector = None

        self.initUI()
        self.history = QD_SceneHistory(self)
        self.clipboard = QD_SceneClipboard(self)

        self.gfx.itemSelected.connect(self.onItemSelected)
        self.gfx.itemsDeselected.connect(self.onItemsDeselected)

    @property
    def has_been_modified(self):
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            # set it now, because we will be reading it soon
            self._has_been_modified = value

            # call all registered listeners
            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value

    def initUI(self):
        self.gfx = self.__class__.SceneGfx_class(self)
        self.gfx.setSceneSize(self.scene_width, self.scene_height)

    def setSilentSelectionEvents(self, value: bool = True):
        """Calling this can suppress onItemSelected events to be triggered. This is usefull when working with clipboard"""
        self._silent_selection_events = value

    def onItemSelected(self, silent: bool = False):
        """
        Handle Item selection and trigger event `Item Selected`

        :param silent: If ``True`` scene's onItemSelected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        if self._silent_selection_events: return

        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            if not silent:
                # we could create some kind of UI which could be serialized,
                # therefore first run all callbacks...
                for callback in self._item_selected_listeners: callback()
                # and store history as a last step always
                self.history.storeHistory("Selection Changed")

    def onItemsDeselected(self, silent: bool = False):
        """
        Handle Items deselection and trigger event `Items Deselected`

        :param silent: If ``True`` scene's onItemsDeselected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        self.resetLastSelectedStates()
        if self._last_selected_items != []:
            self._last_selected_items = []
            if not silent:
                self.history.storeHistory("Deselected Everything")
                for callback in self._items_deselected_listeners: callback()

    def isModified(self) -> bool:
        return self.has_been_modified

    def getSelectedItems(self) -> list:
        """
        Returns currently selected Graphics Items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.gfx.selectedItems()

    def doDeselectItems(self, silent: bool = False) -> None:
        """
        Deselects everything in scene

        :param silent: If ``True`` scene's onItemsDeselected won't be called
        :type silent: ``bool``
        """
        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()

    # our helper listener functions
    def addHasBeenModifiedListener(self, callback: 'function'):
        """
        Register callback for `Has Been Modified` event

        :param callback: callback function
        """
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback: 'function'):
        """
        Register callback for `Item Selected` event

        :param callback: callback function
        """
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback: 'function'):
        """
        Register callback for `Items Deselected` event

        :param callback: callback function
        """
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback: 'function'):
        """
        Register callback for `Drag Enter` event

        :param callback: callback function
        """
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback: 'function'):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self.getView().addDropListener(callback)

    # custom flag to detect node or edge has been selected....
    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.gfx._last_selected_state = False
        for edge in self.edges:
            edge.gfx._last_selected_state = False

    def getView(self) -> 'QGraphicsView':
        return self.gfx.views()[0]

    def getItemAt(self, pos: 'QPointF'):
        return self.getView().itemAt(pos)

    def addNode(self, node: QD_OpNode):
        self.nodes.append(node)

    def addEdge(self, edge: QD_Edge):
        self.edges.append(edge)

    def removeNode(self, node: QD_OpNode):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            if utils.DEBUG:
                print("!W:", "QD_Scene::removeNode", "wanna remove nodeeditor", node, "from self.nodes but it's not in the list!")

    def removeEdge(self, edge: QD_Edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            if confg.DEBUG:
                print("!W:", "QD_Scene::removeEdge", "wanna remove edge", edge, "from self.edges but it's not in the list!")

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()
        self.has_been_modified = False


    def setNodeClassSelector(self, class_selecting_function: 'functon') -> 'QD_OpNode class type':
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data: dict) -> 'QD_OpNode class instance':
        return QD_OpNode if self.node_class_selector is None else self.node_class_selector(data)


    def serialize(self) -> dict:
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        return {
            'id': self.id,
            'scene_width': self.scene_width,
            'scene_height': self.scene_height,
            'nodes': nodes,
            'edges': edges,
        }

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        hashmap = {}

        if restore_id: self.id = data['id']

        # -- deserialize NODES

        ## Instead of recreating all the nodes, reuse existing ones...
        # get list of all current nodes:
        all_nodes = self.nodes.copy()

        # go through deserialized nodes:
        for node_data in data['nodes']:
            # can we find this node in the scene?
            found = False
            for node in all_nodes:
                if node.id == node_data['id']:
                    found = node
                    break

            if not found:
                new_node = self.getNodeClassFromData(node_data)(self)
                new_node.deserialize(node_data, hashmap, restore_id)
                new_node.onDeserialized(node_data)
                # print("New node for", node_data['title'])
            else:
                found.deserialize(node_data, hashmap, restore_id)
                found.onDeserialized(node_data)
                all_nodes.remove(found)
                # print("Reused", node_data['title'])

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_nodes != []:
            node = all_nodes.pop()
            node.remove()

        # -- deserialize EDGES

        ## Instead of recreating all the edges, reuse existing ones...
        # get list of all current edges:
        all_edges = self.edges.copy()

        # go through deserialized edges:
        for edge_data in data['edges']:
            # can we find this node in the scene?
            found = False
            for edge in all_edges:
                if edge.id == edge_data['id']:
                    found = edge
                    break

            if not found:
                new_edge = QD_Edge(self).deserialize(edge_data, hashmap, restore_id)
                # print("New edge for", edge_data)
            else:
                found.deserialize(edge_data, hashmap, restore_id)
                all_edges.remove(found)

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_edges != []:
            edge = all_edges.pop()
            edge.remove()

        return True
