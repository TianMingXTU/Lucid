# src/lucid/debug.py

from .chunk import OpCode


def disassemble_chunk(chunk, name):
    """
    反汇编一个完整的字节码块。
    """
    print(f"== {name} ==")
    offset = 0
    while offset < len(chunk.code):
        offset = disassemble_instruction(chunk, offset)


def disassemble_instruction(chunk, offset):
    """
    反汇编单条指令，并返回下一条指令的偏移量。
    """
    print(f"{offset:04d} ", end="")

    instruction = chunk.code[offset]
    op_name = OpCode(instruction).name

    # 根据指令是否有参数，进行不同的打印
    if instruction in (
        OpCode.OP_CONSTANT,
        OpCode.OP_DEFINE_GLOBAL,
        OpCode.OP_GET_GLOBAL,
    ):
        # 这些指令有一个1字节的参数（常量池索引）
        constant_index = chunk.code[offset + 1]
        constant_value = chunk.constants[constant_index]
        print(f"{op_name:<16} {constant_index:4d} '{constant_value}'")
        return offset + 2
    else:
        # 无参数指令
        print(f"{op_name}")
        return offset + 1
