# run_tests.py (Upgraded for v3.3)
import sys
import time
from src.lucid.lexer import Lexer
from src.lucid.parser import Parser
from src.lucid.interpreter import Interpreter, UnitValue, Unit, OkValue, ErrValue, Task

TEST_CASES = [
    # ... (All previous 16 tests remain) ...
    {
        "name": "Recursive Function",
        "source": "let factorial = fn(n) { if n == 0 then 1 else { n * factorial(n - 1) } }; factorial(5)",
        "expected": 120,
    },
    {
        "name": "Complex Unit Expression",
        "source": "let force = 10*kg*m/(s^2); force",
        "expected": OkValue(UnitValue(10, Unit(["kg", "m"], ["s", "s"]))),
    },
    {
        "name": "Result: Successful Division",
        "source": "100 / 10",
        "expected": OkValue(UnitValue(10, Unit())),
    },
    {
        "name": "Pipe: Short-circuit on Err",
        "source": "let double = fn(x){x*2}; (100/0) |> double",
        "expected": ErrValue("Division by zero"),
    },
    {
        "name": "Builtin: unwrap_or() with Err",
        "source": 'unwrap_or(Err("oops"), -1)',
        "expected": -1,
    },
    # --- v3.3 NEW: Concurrency Logic Tests ---
    {
        "name": "Concurrency: Spawn returns a task",
        "source": "spawn { 1+1 }",
        "expected": Task(None),
    },
    {
        "name": "Concurrency: Await executes a task",
        "source": "let my_task = spawn { 10 * 2 }; await my_task",
        "expected": 20,
    },
    {
        "name": "Concurrency: Await a value (fail)",
        "source": "await 10",
        "expected": "TypeError: await can only be used on a task",
    },
    {
        "name": "Concurrency: Task with return",
        "source": "let t = spawn { return 50; 100 }; await t",
        "expected": 50,
    },
    {
        "name": "Concurrency: Task captures environment",
        "source": "let x = 10; let t = spawn { x * x }; await t",
        "expected": 100,
    },
]


def compare_results(result, expected):
    if isinstance(expected, Task):
        return isinstance(result, Task)
    if (
        isinstance(result, UnitValue)
        and not result.unit.numerators
        and not result.unit.denominators
    ):
        result = result.value
    if isinstance(result, OkValue):
        if (
            isinstance(result.value, UnitValue)
            and not result.value.unit.numerators
            and not result.value.unit.denominators
        ):
            result = OkValue(result.value.value)
    if isinstance(expected, str) and expected.startswith("TypeError:"):
        return isinstance(result, TypeError) and str(result) == expected.replace(
            "TypeError: ", ""
        )
    return result == expected


def run_all_tests():
    print("=" * 50)
    print("  Running Lucid Language Test Suite v3.3")
    print("=" * 50)
    passed_count = 0
    failed_count = 0
    # A single interpreter to run all tests
    interpreter = Interpreter()
    for i, case in enumerate(TEST_CASES):
        name, source, expected = case["name"], case["source"], case["expected"]
        print(f"[{i+1:02d}] Running test: {name: <45}", end="")
        result_val = None
        try:
            lexer = Lexer(source)
            parser = Parser(lexer)
            ast = parser.parse()
            # We use the same interpreter to allow 'let' statements to define vars for later tests
            result_val = interpreter.visit(ast)
            if compare_results(result_val, expected):
                print("\033[92m [PASS] \033[0m")
                passed_count += 1
            else:
                print("\033[91m [FAIL] \033[0m")
                print(
                    f"      - Source:   {source}\n      - Expected: {repr(expected)}\n      - Got:      {repr(result_val)}"
                )
                failed_count += 1
        except Exception as e:
            if (
                isinstance(expected, str)
                and expected.startswith(type(e).__name__ + ":")
                and str(e) in expected
            ):
                print("\033[92m [PASS] (Correctly caught error)\033[0m")
                passed_count += 1
            else:
                print("\033[91m [ERROR] \033[0m")
                print(
                    f"      - Source: {source}\n      - Expected: {repr(expected)}\n      - Exception: {type(e).__name__}: {e}"
                )
                failed_count += 1

    # Clean up the thread pool
    interpreter.executor.shutdown(wait=True)

    print("-" * 50)
    print("Test Summary:")
    print(f"\033[92m  Passed: {passed_count}\033[0m")
    if failed_count > 0:
        print(f"\033[91m  Failed: {failed_count}\033[0m")
    print("=" * 50)
    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
