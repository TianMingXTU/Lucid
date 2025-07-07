# src/lucid/vm.py
import enum
from .chunk import Chunk, OpCode
from .runtime_types import Unit, UnitValue

VMResult = enum.Enum("VMResult", ["OK", "COMPILE_ERROR", "RUNTIME_ERROR"])


class VM:
    """
    Lucid 字节码虚拟机。(v4.2 - 最终稳定版)
    """

    def __init__(self):
        self.chunk = None
        self.ip = 0
        self.stack = []
        self.globals = {}

    def interpret(self, chunk):
        self.chunk = chunk
        self.ip = 0
        self.stack = []

        result = self.run()

        if result == VMResult.OK:
            return self.pop() if self.stack else None

        return result

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def peek(self, distance=0):
        return self.stack[-1 - distance]

    def is_falsy(self, value):
        return value is None or value is False

    def run(self):
        while self.ip < len(self.chunk.code):
            instruction = OpCode(self.chunk.code[self.ip])
            self.ip += 1

            if instruction == OpCode.OP_CONSTANT:
                constant_index = self.chunk.code[self.ip]
                self.ip += 1
                self.push(self.chunk.constants[constant_index])

            elif instruction == OpCode.OP_TRUE:
                self.push(True)
            elif instruction == OpCode.OP_FALSE:
                self.push(False)
            elif instruction == OpCode.OP_NIL:
                self.push(None)

            elif instruction == OpCode.OP_POP:
                self.pop()

            elif instruction == OpCode.OP_DEFINE_GLOBAL:
                # *** BUG FIX: Change from peek() back to pop() ***
                # The instruction's job is to consume the value from the stack and store it.
                var_name_index = self.chunk.code[self.ip]
                self.ip += 1
                self.globals[self.chunk.constants[var_name_index]] = self.pop()

            elif instruction == OpCode.OP_GET_GLOBAL:
                var_name_index = self.chunk.code[self.ip]
                self.ip += 1
                var_name = self.chunk.constants[var_name_index]
                value = self.globals.get(var_name)
                if value is None:
                    self.push(UnitValue(1, Unit([var_name])))
                else:
                    self.push(value)

            elif instruction == OpCode.OP_BUILD_UNIT_VALUE:
                unit_string, number_value = self.pop(), self.pop()
                self.push(UnitValue(number_value, Unit([unit_string])))

            elif instruction == OpCode.OP_JUMP_IF_FALSE:
                jump_offset = (self.chunk.code[self.ip] << 8) | self.chunk.code[
                    self.ip + 1
                ]
                self.ip += 2
                if self.is_falsy(self.peek()):
                    self.ip += jump_offset

            elif instruction == OpCode.OP_JUMP:
                jump_offset = (self.chunk.code[self.ip] << 8) | self.chunk.code[
                    self.ip + 1
                ]
                self.ip += 2
                self.ip += jump_offset

            elif instruction == OpCode.OP_EQUAL:
                b, a = self.pop(), self.pop()
                self.push(a == b)

            elif instruction == OpCode.OP_GREATER or instruction == OpCode.OP_LESS:
                b, a = self.pop(), self.pop()
                val_a = a if isinstance(a, UnitValue) else UnitValue(a, Unit())
                val_b = b if isinstance(b, UnitValue) else UnitValue(b, Unit())
                if val_a.unit != val_b.unit:
                    raise TypeError("Cannot compare values with different units.")
                if instruction == OpCode.OP_GREATER:
                    self.push(val_a.value > val_b.value)
                else:
                    self.push(val_a.value < val_b.value)

            elif (
                instruction == OpCode.OP_ADD
                or instruction == OpCode.OP_SUBTRACT
                or instruction == OpCode.OP_MULTIPLY
                or instruction == OpCode.OP_DIVIDE
                or instruction == OpCode.OP_POWER
            ):
                b, a = self.pop(), self.pop()
                val_a = a if isinstance(a, UnitValue) else UnitValue(a, Unit())
                val_b = b if isinstance(b, UnitValue) else UnitValue(b, Unit())
                if instruction == OpCode.OP_ADD:
                    if val_a.unit != val_b.unit:
                        raise TypeError("Incompatible units for addition.")
                    result = UnitValue(val_a.value + val_b.value, val_a.unit)
                elif instruction == OpCode.OP_SUBTRACT:
                    if val_a.unit != val_b.unit:
                        raise TypeError("Incompatible units for subtraction.")
                    result = UnitValue(val_a.value - val_b.value, val_a.unit)
                elif instruction == OpCode.OP_MULTIPLY:
                    result = UnitValue(
                        val_a.value * val_b.value,
                        Unit(
                            val_a.unit.numerators + val_b.unit.numerators,
                            val_a.unit.denominators + val_b.unit.denominators,
                        ),
                    )
                elif instruction == OpCode.OP_DIVIDE:
                    if val_b.value == 0:
                        raise ZeroDivisionError("Division by zero.")
                    result = UnitValue(
                        val_a.value / val_b.value,
                        Unit(
                            val_a.unit.numerators + val_b.unit.denominators,
                            val_a.unit.denominators + val_b.unit.numerators,
                        ),
                    )
                elif instruction == OpCode.OP_POWER:
                    if val_b.unit.numerators or val_b.unit.denominators:
                        raise TypeError("Exponent must be a scalar.")
                    new_num = {
                        u: p * val_b.value for u, p in val_a.unit.numerators.items()
                    }
                    new_den = {
                        u: p * val_b.value for u, p in val_a.unit.denominators.items()
                    }
                    result = UnitValue(val_a.value**val_b.value, Unit(new_num, new_den))

                if not result.unit.numerators and not result.unit.denominators:
                    self.push(result.value)
                else:
                    self.push(result)

            elif instruction == OpCode.OP_NOT:
                self.push(self.is_falsy(self.pop()))
            elif instruction == OpCode.OP_NEGATE:
                value = self.pop()
                self.push(
                    UnitValue(-value.value, value.unit)
                    if isinstance(value, UnitValue)
                    else -value
                )

            elif instruction == OpCode.OP_RETURN:
                return VMResult.OK

        return VMResult.OK
