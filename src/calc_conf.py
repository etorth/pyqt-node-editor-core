LISTBOX_MIMETYPE = "application/x-item"

OP_NODE_INPUT = 1
OP_NODE_OUTPUT = 2
OP_NODE_ADD = 3
OP_NODE_SUB = 4
OP_NODE_MUL = 5
OP_NODE_DIV = 6
OP_NODE_CHECKER = 7
OP_NODE_EDITOR = 8

CALC_NODES = {}


class ConfException(Exception):
    pass


class InvalidNodeRegistration(ConfException):
    pass


class OpCodeNotRegistered(ConfException):
    pass


def register_node_now(class_reference):
    if class_reference.op_code in CALC_NODES:
        raise InvalidNodeRegistration("Duplicite node registration of '%s'. There is already %s" % (class_reference.op_code, CALC_NODES[class_reference.op_code]))
    CALC_NODES[class_reference.op_code] = class_reference


def register_node(original_class):
    register_node_now(original_class)
    return original_class


def get_class_from_opcode(op_code):
    if op_code not in CALC_NODES:
        raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return CALC_NODES[op_code]


from nodes import *
