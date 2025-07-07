# src/lucid/runtime_types.py
from collections import Counter


class OkValue:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Ok({repr(self.value)})"

    def __eq__(self, other):
        return isinstance(other, OkValue) and self.value == other.value


class ErrValue:
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f"Err('{self.message}')"

    def __eq__(self, other):
        return isinstance(other, ErrValue) and self.message == other.message


class Unit:
    def __init__(self, numerators=None, denominators=None):
        self.numerators = Counter(numerators or [])
        self.denominators = Counter(denominators or [])
        self._simplify()

    def _simplify(self):
        common = self.numerators & self.denominators
        self.numerators -= common
        self.denominators -= common

    def __repr__(self):
        def format_part(counter):
            parts = [
                f"{unit}^{power}" if power > 1 else unit
                for unit, power in sorted(counter.items())
            ]
            return "*".join(parts)

        num_str = format_part(self.numerators) or "1"
        den_str = format_part(self.denominators)
        if not den_str:
            return num_str
        is_simple_den = (
            len(self.denominators) == 1 and self.denominators.most_common(1)[0][1] == 1
        )
        return f"{num_str}/{den_str}" if is_simple_den else f"{num_str}/({den_str})"

    def __eq__(self, other):
        return (
            isinstance(other, Unit)
            and self.numerators == other.numerators
            and self.denominators == other.denominators
        )


class UnitValue:
    def __init__(self, value, unit_obj):
        self.value, self.unit = value, unit_obj

    def __repr__(self):
        return (
            str(self.value)
            if not self.unit.numerators and not self.unit.denominators
            else f"{self.value}{self.unit}"
        )

    def __eq__(self, other):
        if isinstance(other, int):
            return (
                self.value == other
                and not self.unit.numerators
                and not self.unit.denominators
            )
        return (
            isinstance(other, UnitValue)
            and self.value == other.value
            and self.unit == other.unit
        )


class Function:
    def __init__(self, parameters, body, env):
        self.parameters, self.body, self.env = parameters, body, env

    def __repr__(self):
        return f"<Function {len(self.parameters)} args>"


class BuiltinFunction:
    def __init__(self, fn, name="<builtin>"):
        self.fn, self.name = fn, name

    def __repr__(self):
        return f"<Builtin Function: {self.name}>"


class Task:
    def __init__(self, future):
        self.future = future

    def __repr__(self):
        return f"<Task running={self.future.running()}>"


class ReturnValue:
    def __init__(self, value):
        self.value = value
