# src/lucid/interpreter.py
from .ast import *
from collections import Counter


# ... (All previous runtime classes: OkValue, ErrValue, Unit, etc. are unchanged) ...
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


# *** NEW: Task object for concurrency ***
class Task:
    def __init__(self, block, env):
        self.block = block
        self.env = env  # The environment where the task was spawned

    def __repr__(self):
        return "<Task>"


class Environment:
    def __init__(self, outer=None):
        self.store, self.outer = {}, outer

    def get(self, name):
        val = self.store.get(name)
        return val if val is not None or self.outer is None else self.outer.get(name)

    def set(self, name, val):
        self.store[name] = val
        return val


class ReturnValue:
    def __init__(self, value):
        self.value = value


class NodeVisitor:
    def visit(self, node):
        if node is None:
            return None
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined")


class Interpreter(NodeVisitor):
    def __init__(self):
        self.env = Environment()
        self._populate_builtins()

    def _populate_builtins(self):
        self.env.set("Ok", BuiltinFunction(lambda value: OkValue(value), "Ok"))
        # ... (other builtins)
        self.env.set("Err", BuiltinFunction(lambda msg: ErrValue(msg), "Err"))
        self.env.set(
            "is_ok", BuiltinFunction(lambda arg: isinstance(arg, OkValue), "is_ok")
        )
        self.env.set(
            "is_err", BuiltinFunction(lambda arg: isinstance(arg, ErrValue), "is_err")
        )
        self.env.set(
            "unwrap_or",
            BuiltinFunction(
                lambda res, default: res.value if isinstance(res, OkValue) else default,
                "unwrap_or",
            ),
        )
        self.env.set(
            "print", BuiltinFunction(lambda arg: print(arg) or OkValue(None), "print")
        )

    # ... (visit_BlockStatement, visit_BinOp, visit_UnaryOp, etc. are unchanged) ...
    def visit_BlockStatement(self, node):
        last_result = None
        for statement in node.statements:
            result = self.visit(statement)
            if isinstance(result, ReturnValue):
                return result
            last_result = result
        return last_result

    def visit_BinOp(self, node):
        op = node.op.type
        if op == "PIPE":
            left_val = self.visit(node.left)
            if isinstance(left_val, ErrValue):
                return left_val
            value_to_pipe = (
                left_val.value if isinstance(left_val, OkValue) else left_val
            )
            right_func = self.visit(node.right)
            return self._apply_function(right_func, [value_to_pipe])
        left_unwrapped = self.visit(node.left)
        right_unwrapped = self.visit(node.right)
        left = (
            left_unwrapped
            if isinstance(left_unwrapped, UnitValue)
            else UnitValue(left_unwrapped, Unit())
        )
        right = (
            right_unwrapped
            if isinstance(right_unwrapped, UnitValue)
            else UnitValue(right_unwrapped, Unit())
        )
        if not (isinstance(left, UnitValue) and isinstance(right, UnitValue)):
            if (
                op == "PLUS"
                and isinstance(left_unwrapped, str)
                and isinstance(right_unwrapped, str)
            ):
                return str(left_unwrapped) + str(right_unwrapped)
            raise TypeError(f"Unsupported operation '{op}' on non-numeric types")
        l_unit, r_unit = left.unit, right.unit
        l_val, r_val = left.value, right.value
        if op == "PLUS" or op == "MINUS":
            if l_unit != r_unit:
                raise TypeError(
                    f"Cannot perform {op} on incompatible units: {l_unit} and {r_unit}"
                )
            return UnitValue(l_val + r_val if op == "PLUS" else l_val - r_val, l_unit)
        elif op == "MUL":
            new_unit = Unit(
                l_unit.numerators + r_unit.numerators,
                l_unit.denominators + r_unit.denominators,
            )
            return UnitValue(l_val * r_val, new_unit)
        elif op == "DIV":
            if r_val == 0:
                return ErrValue("Division by zero")
            return OkValue(
                UnitValue(
                    l_val // r_val,
                    Unit(
                        l_unit.numerators + r_unit.denominators,
                        l_unit.denominators + r_unit.numerators,
                    ),
                )
            )
        elif op == "CARET":
            if r_unit.numerators or r_unit.denominators:
                raise TypeError("Exponent must be a scalar (dimensionless) number")
            new_numerators = {
                unit: power * r_val for unit, power in l_unit.numerators.items()
            }
            new_denominators = {
                unit: power * r_val for unit, power in l_unit.denominators.items()
            }
            return UnitValue(l_val**r_val, Unit(new_numerators, new_denominators))
        elif op in ("EQ", "NE", "GT", "GTE", "LT", "LTE"):
            if l_unit != r_unit:
                raise TypeError(
                    f"Cannot compare values with different units: {l_unit} and {r_unit}"
                )
            ops = {
                "EQ": "__eq__",
                "NE": "__ne__",
                "GT": "__gt__",
                "GTE": "__ge__",
                "LT": "__lt__",
                "LTE": "__le__",
            }
            return getattr(l_val, ops[op])(r_val)
        raise TypeError(f"Unsupported operation '{op}'")

    def visit_VarAccess(self, node):
        var_name = node.var_name
        val = self.env.get(var_name)
        if val is None:
            return UnitValue(1, Unit([var_name]))
        return val

    def visit_Num(self, node):
        return node.value

    def visit_Boolean(self, node):
        return node.value

    def visit_StringLiteral(self, node):
        return node.value

    def visit_UnitNumber(self, node):
        return UnitValue(node.value, Unit([node.unit]))

    def visit_UnaryOp(self, node):
        op = node.op.type
        val = self.visit(node.expr)
        if op == "PLUS":
            return val
        if op == "MINUS":
            if isinstance(val, UnitValue):
                return UnitValue(-val.value, val.unit)
            return -val

    def visit_IfExpression(self, node):
        condition = self.visit(node.condition)
        if isinstance(condition, OkValue):
            condition = condition.value
        if not isinstance(condition, bool):
            raise TypeError("If condition must be a boolean value")
        return (
            self.visit(node.then_branch) if condition else self.visit(node.else_branch)
        )

    def visit_VarAssign(self, node):
        value = self.visit(node.value_node)
        self.env.set(node.var_name, value)
        return None

    def visit_FunctionLiteral(self, node):
        return Function(node.parameters, node.body, self.env)

    # *** NEW: Concurrency visit methods ***
    def visit_SpawnExpression(self, node):
        # For now, just create a Task object. No real concurrency yet.
        return Task(node.block, self.env)

    def visit_AwaitExpression(self, node):
        task = self.visit(node.task_expr)
        if not isinstance(task, Task):
            raise TypeError("await can only be used on a task")

        # In this version, we execute the task sequentially.
        # We create a new environment for the task, based on where it was spawned.
        task_env = Environment(outer=task.env)

        # Temporarily switch to the task's environment to execute its block
        original_env = self.env
        self.env = task_env
        result = self.visit(task.block)
        self.env = original_env

        if isinstance(result, ReturnValue):
            return result.value
        return result

    def _apply_function(self, func, args):
        if isinstance(func, BuiltinFunction):
            try:
                return func.fn(*args)
            except TypeError as e:
                raise TypeError(f"Built-in function error: {e}")
        if not isinstance(func, Function):
            raise TypeError("Can only call functions")
        if len(args) != len(func.parameters):
            raise TypeError(
                f"Expected {len(func.parameters)} arguments, got {len(args)}"
            )

        call_env, original_env = Environment(outer=func.env), self.env
        for param, arg in zip(func.parameters, args):
            call_env.set(param.value, arg)

        self.env = call_env
        result = self.visit(func.body)
        self.env = original_env
        return result.value if isinstance(result, ReturnValue) else result

    def visit_CallExpression(self, node):
        func = self.visit(node.function)
        args = [self.visit(arg) for arg in node.arguments]
        return self._apply_function(func, args)

    def visit_ReturnStatement(self, node):
        return ReturnValue(self.visit(node.return_value))

    def interpret(self, tree):
        return self.visit(tree)
