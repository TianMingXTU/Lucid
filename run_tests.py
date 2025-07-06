# run_tests.py (Final version for v3.0)
import sys
from src.lucid.lexer import Lexer
from src.lucid.parser import Parser
from src.lucid.interpreter import Interpreter, UnitValue, Unit

TEST_CASES = [
    {"name": "Simple Addition", "source": "10 + 5", "expected": 15},
    {"name": "Operator Precedence", "source": "10 + 2 * 3", "expected": 16},
    {
        "name": "Recursive Function",
        "source": "let factorial = fn(n) { if n == 0 then 1 else { n * factorial(n - 1) } }; factorial(5)",
        "expected": 120,
    },
    {
        "name": "Unit Addition",
        "source": "10*m + 5*m",
        "expected": UnitValue(15, Unit(["m"])),
    },
    {
        "name": "Unit Multiplication by Scalar",
        "source": "10*kg * 3",
        "expected": UnitValue(30, Unit(["kg"])),
    },
    {"name": "Unit Comparison", "source": "100*m > 50*m", "expected": True},
    {
        "name": "Unit Multiplication (Area)",
        "source": "10*m * 5*m",
        "expected": UnitValue(50, Unit(["m", "m"])),
    },
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
    {"name": "Exponentiation (Scalar)", "source": "2^3", "expected": 8},
    {
        "name": "Exponentiation (Unit)",
        "source": "(10*m)^2",
        "expected": UnitValue(100, Unit(["m", "m"])),
    },
    {
        "name": "Exponentiation (Right-associativity)",
        "source": "2^3^2",
        "expected": 512,
    },
    {
        "name": "Exponentiation (Fail with unit exponent)",
        "source": "10*m^(2*s)",
        "expected": "TypeError: Exponent must be a scalar (dimensionless) number",
    },
    {
        "name": "Complex Unit Expression",
        "source": "let force = 10*kg*m/(s^2); force",
        "expected": UnitValue(10, Unit(["kg", "m"], ["s", "s"])),
    },
]


def compare_results(result, expected):
    if (
        isinstance(result, UnitValue)
        and not result.unit.numerators
        and not result.unit.denominators
    ):
        result = result.value
    if isinstance(expected, str) and expected.startswith("TypeError:"):
        return isinstance(result, TypeError) and str(result) == expected.replace(
            "TypeError: ", ""
        )
    return result == expected


def run_all_tests():
    print("=" * 50)
    print("  Running Lucid Language Test Suite v3.0")
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
