# src/lucid/chunk.py

import enum


class OpCode(enum.IntEnum):
    """
    定义虚拟机可以理解的指令操作码。(v6 - 支持if/else)
    """

    # --- 常量操作 ---
    OP_CONSTANT = 0

    # --- 字面量与布尔逻辑 ---
    OP_NIL = 1
    OP_TRUE = 2
    OP_FALSE = 3
    OP_EQUAL = 4
    OP_GREATER = 5
    OP_LESS = 6
    OP_NOT = 7

    # --- 算术运算符 ---
    OP_ADD = 8
    OP_SUBTRACT = 9
    OP_MULTIPLY = 10
    OP_DIVIDE = 11
    OP_POWER = 12
    OP_NEGATE = 13

    # --- 语句与返回 ---
    OP_POP = 14
    OP_RETURN = 15
    OP_BUILD_UNIT_VALUE = 16

    # --- 变量操作 ---
    OP_DEFINE_GLOBAL = 17
    OP_GET_GLOBAL = 18

    # --- 跳转指令 ---
    OP_JUMP_IF_FALSE = 19
    OP_JUMP = 20


class Chunk:
    """
    一个 Chunk 代表一段编译好的字节码。
    它包含了指令序列和与之关联的常量池。
    """

    def __init__(self):
        self.code = bytearray()
        self.constants = []

    def write_byte(self, byte):
        """写入单个字节到 code 中"""
        self.code.append(byte)

    def add_constant(self, value):
        """
        将一个常量添加到常量池中，并返回其索引。
        如果常量已存在，则直接返回现有索引。
        """
        # 为了简化，我们暂时允许重复，因为处理不可哈希的类型（如列表）作为常量会更复杂
        self.constants.append(value)
        return len(self.constants) - 1

    def write_constant(self, value):
        """
        一个辅助方法，用于方便地添加常量并写入 OP_CONSTANT 指令。
        """
        constant_index = self.add_constant(value)
        if constant_index > 255:
            raise ValueError("Constant index exceeds 256 limit.")
        self.write_byte(OpCode.OP_CONSTANT)
        self.write_byte(constant_index)
