# -*- coding: utf-8 -*-
"""A module containing base class for Node's content graphical representation. It also contains example of
overriden Text Widget which can pass to it's parent notification about currently being modified."""
from collections import OrderedDict
from node_serializable import Serializable
from PyQt6.QtWidgets import *


class QDMNodeContentWidget(QWidget, Serializable):
    """Base class for representation of the Node's graphics content. This class also provides layout for other widgets inside of a :py:class:`~nodeeditor.node.Node`
    """

    def __init__(self, node: 'Node', parent: QGraphicsWidget = None):
        """:param node: reference to the :py:class:`~nodeeditor.node.Node`
        :type node: :py:class:`~nodeeditor.node.Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:
            - **node** - reference to the :class:`~nodeeditor.node.Node`
            - **layout** - ``QLayout`` container
        """
        self.node = node
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        """Sets up layouts and widgets to be rendered in :py:class:`~nodeeditor.nodegfx.NodeGfx` class.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


    def setEditingFlag(self, value: bool):
        """
        .. note::

            If you are handling keyPress events by default Qt Window's shortcuts and ``QActions``, you will not
            probably need to use this method

        Helper function which sets editingFlag inside :py:class:`~nodeeditor.node_graphics_view.GfxView` class.

        This is a helper function to handle keys inside nodes with ``QLineEdits`` or ``QTextEdits`` (you can
        use overriden :py:class:`QDMTextEdit` class) and with QGraphicsView class method ``keyPressEvent``.

        :param value: new value for editing flag
        """
        self.node.scene.getView().editingFlag = value

    def serialize(self) -> OrderedDict:
        return OrderedDict([])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        return True


class QDMTextEdit(QTextEdit):
    """
        .. note::

            This class is example of ``QTextEdit`` modification to be able to handle `Delete` key with overriden
            Qt's ``keyPressEvent`` (when not using ``QActions`` in menu or toolbar)

        Overriden ``QTextEdit`` which sends notification about being edited to parent's container :py:class:`QDMNodeContentWidget`
    """

    def focusInEvent(self, event: 'QFocusEvent'):
        """Example of overriden focusInEvent to mark start of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: 'QFocusEvent'):
        """Example of overriden focusOutEvent to mark end of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
