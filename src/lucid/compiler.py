# src/lucid/compiler.py

from .ast import *
from .chunk import Chunk, OpCode
from .core_types import Token


class Compiler:
    """
    编译器，负责将 AST 翻译成字节码。(v3.5 - 稳定版)
    """

    def __init__(self):
        self.chunk = None

    def compile(self, program_node):
        self.chunk = Chunk()
        self.visit(program_node)
        self.emit_byte(OpCode.OP_RETURN)
        return self.chunk

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(
            f"Compiler Error: No visit_{type(node).__name__} method defined for {node}"
        )

    # --- 辅助方法 ---
    def emit_byte(self, byte):
        self.chunk.write_byte(byte)

    def emit_bytes(self, byte1, byte2):
        self.emit_byte(byte1)
        self.emit_byte(byte2)

    def emit_constant(self, value):
        self.chunk.write_constant(value)

    def emit_jump(self, instruction):
        self.emit_byte(instruction)
        self.emit_byte(0xFF)
        self.emit_byte(0xFF)
        return len(self.chunk.code) - 2

    def patch_jump(self, offset):
        jump = len(self.chunk.code) - offset - 2
        if jump > 65535:
            raise ValueError("Too much code to jump over.")
        self.chunk.code[offset] = (jump >> 8) & 0xFF
        self.chunk.code[offset + 1] = jump & 0xFF

    # --- 节点访问者 ---
    def visit_BlockStatement(self, node):
        statements = node.statements
        for i, statement in enumerate(statements):
            self.visit(statement)
            # If it's an expression statement and not the last one, pop its value.
            # let statements are handled in visit_VarAssign.
            if not isinstance(statement, VarAssign) and i < len(statements) - 1:
                self.emit_byte(OpCode.OP_POP)

    def visit_VarAssign(self, node):
        self.visit(node.value_node)
        var_name_index = self.chunk.add_constant(node.var_name)
        self.emit_bytes(OpCode.OP_DEFINE_GLOBAL, var_name_index)
        # *** BUG FIX: After a `let` statement, the value should be consumed. ***
        # However, since the VM's OP_DEFINE_GLOBAL will now pop it,
        # we don't need an extra pop here. This logic is now cleaner.

    def visit_VarAccess(self, node):
        var_name_index = self.chunk.add_constant(node.var_name)
        self.emit_bytes(OpCode.OP_GET_GLOBAL, var_name_index)

    def visit_IfExpression(self, node):
        self.visit(node.condition)
        else_jump = self.emit_jump(OpCode.OP_JUMP_IF_FALSE)
        self.emit_byte(OpCode.OP_POP)
        self.visit(node.then_branch)
        end_jump = self.emit_jump(OpCode.OP_JUMP)
        self.patch_jump(else_jump)
        if node.else_branch is not None:
            self.visit(node.else_branch)
        else:
            self.emit_byte(OpCode.OP_NIL)
        self.patch_jump(end_jump)

    def visit_Num(self, node):
        self.emit_constant(node.value)

    def visit_StringLiteral(self, node):
        self.emit_constant(node.value)

    def visit_Boolean(self, node):
        if node.value:
            self.emit_byte(OpCode.OP_TRUE)
        else:
            self.emit_byte(OpCode.OP_FALSE)

    def visit_UnitNumber(self, node):
        self.emit_constant(node.value)
        self.emit_constant(node.unit)
        self.emit_byte(OpCode.OP_BUILD_UNIT_VALUE)

    def visit_UnaryOp(self, node):
        self.visit(node.expr)
        op_type = node.op.type
        if op_type == "MINUS":
            self.emit_byte(OpCode.OP_NEGATE)
        elif op_type == "PLUS":
            pass
        else:
            raise NotImplementedError(f"Unary operator '{op_type}' not supported.")

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        op_type = node.op.type
        if op_type == "PLUS":
            self.emit_byte(OpCode.OP_ADD)
        elif op_type == "MINUS":
            self.emit_byte(OpCode.OP_SUBTRACT)
        elif op_type == "MUL":
            self.emit_byte(OpCode.OP_MULTIPLY)
        elif op_type == "DIV":
            self.emit_byte(OpCode.OP_DIVIDE)
        elif op_type == "CARET":
            self.emit_byte(OpCode.OP_POWER)
        elif op_type == "EQ":
            self.emit_byte(OpCode.OP_EQUAL)
        elif op_type == "NE":
            self.emit_byte(OpCode.OP_EQUAL)
            self.emit_byte(OpCode.OP_NOT)
        elif op_type == "GT":
            self.emit_byte(OpCode.OP_GREATER)
        elif op_type == "GTE":
            self.emit_byte(OpCode.OP_LESS)
            self.emit_byte(OpCode.OP_NOT)
        elif op_type == "LT":
            self.emit_byte(OpCode.OP_LESS)
        elif op_type == "LTE":
            self.emit_byte(OpCode.OP_GREATER)
            self.emit_byte(OpCode.OP_NOT)
        else:
            raise NotImplementedError(
                f"Binary operator '{op_type}' not supported by compiler."
            )
