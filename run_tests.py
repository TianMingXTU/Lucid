# run_tests.py (Upgraded for v3.2)
import sys
from src.lucid.lexer import Lexer
from src.lucid.parser import Parser
from src.lucid.interpreter import Interpreter, UnitValue, Unit, OkValue, ErrValue

TEST_CASES = [
    # --- Basic Sanity Checks ---
    {
        "name": "Recursive Function",
        "source": "let factorial = fn(n) { if n == 0 then 1 else { n * factorial(n - 1) } }; factorial(5)",
        "expected": 120,
    },
    # --- Division now returns direct values on success ---
    {"name": "Successful Division", "source": "100 / 10", "expected": 10},
    {
        "name": "Failed Division",
        "source": "100 / 0",
        "expected": ErrValue("Division by zero"),
    },
    # --- Pipe Tests ---
    {
        "name": "Pipe: Simple Pipe",
        "source": "let double = fn(x){x*2}; 10 |> double",
        "expected": 20,
    },
    {
        "name": "Pipe: Chained Pipe",
        "source": "let inc = fn(x){x+1}; let dbl = fn(x){x*2}; 5 |> inc |> dbl",
        "expected": 12,
    },
    {
        "name": "Pipe: Short-circuit on Err",
        "source": "let double = fn(x){x*2}; (100/0) |> double",
        "expected": ErrValue("Division by zero"),
    },
    # --- Unit System Tests (now expect direct UnitValues) ---
    {
        "name": "Unit Division (Speed)",
        "source": "100*km / (10*hr)",
        "expected": UnitValue(10, Unit(["km"], ["hr"])),
    },
    {
        "name": "Unit Division (Cancellation)",
        "source": "100*m*m / (10*m)",
        "expected": UnitValue(10, Unit(["m"])),
    },
    {
        "name": "Complex Unit Expression",
        "source": "let force = 10*kg*m/(s^2); force",
        "expected": UnitValue(10, Unit(["kg", "m"], ["s", "s"])),
    },
    # --- Builtin Function Tests ---
    {"name": "Builtin: Ok()", "source": "Ok(100)", "expected": OkValue(100)},
    {
        "name": "Builtin: Err()",
        "source": 'Err("file not found")',
        "expected": ErrValue("file not found"),
    },
    {"name": "Builtin: is_ok() True", "source": "is_ok(Ok(10))", "expected": True},
]


def compare_results(result, expected):
    # Unpack unitless values for easier comparison
    if (
        isinstance(result, UnitValue)
        and not result.unit.numerators
        and not result.unit.denominators
    ):
        result = result.value
    return result == expected


def run_all_tests():
    print("=" * 50)
    print("  Running Lucid Language Test Suite v3.2")
    print("=" * 50)
    passed_count = 0
    failed_count = 0
    for i, case in enumerate(TEST_CASES):
        name, source, expected = case["name"], case["source"], case["expected"]
        print(f"[{i+1:02d}] Running test: {name: <45}", end="")
        result_val = None
        try:
            lexer = Lexer(source)
            parser = Parser(lexer)
            ast = parser.parse()
            interpreter = Interpreter()
            result_val = interpreter.interpret(ast)
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
            # A simple way to check for expected errors
            if (
                isinstance(expected, ErrValue)
                and isinstance(e, TypeError)
                and expected.message in str(e)
            ):
                print("\033[92m [PASS] (Correctly caught error)\033[0m")
                passed_count += 1
            elif expected == e:
                print("\033[92m [PASS] (Correctly caught error)\033[0m")
                passed_count += 1
            else:
                print("\033[91m [ERROR] \033[0m")
                print(
                    f"      - Source: {source}\n      - Expected: {repr(expected)}\n      - Exception: {type(e).__name__}: {e}"
                )
                failed_count += 1
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
