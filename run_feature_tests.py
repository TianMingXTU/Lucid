# run_feature_tests.py

import sys
from io import StringIO

# 这是一个技巧，确保脚本可以找到 src 目录下的模块
sys.path.insert(0, "./src")

from lucid.lexer import Lexer
from lucid.parser import Parser
from lucid.compiler import Compiler
from lucid.vm import VM
from lucid.runtime_types import UnitValue

# --- 测试用例定义 ---
# 格式: ("描述", "Lucid 代码", "期望的 repr() 输出")
# 对于非字符串的期望值，脚本会自动调用 repr()
TEST_CASES = [
    # --- 基础运算 ---
    ("Simple Addition", "5 + 10", "15"),
    ("Operator Precedence", "5 + 10 * 2", "25"),
    ("Parentheses", "(5 + 10) * 2", "30"),
    ("Negative Numbers", "-10", "-10"),
    # --- 单位系统 ---
    ("Unit Creation", "10m", "10m"),
    ("Unit Multiplication", "10m * 5s", "50m*s"),
    ("Unit Division", "100km / 2hr", "50.0km/hr"),
    ("Unit Power", "10m^2", "100m^2"),  # 注意：10m^2 解析为 (10m)^2
    # --- 变量 ---
    ("Variable Assignment", "let a = 100", "None"),
    ("Variable Access", "a", "100"),
    ("Variable in Expression", "a / 5", "20.0"),
    # --- 比较运算 ---
    ("Equality True", "10 == 10", "True"),
    ("Equality False", "10 == 9", "False"),
    ("Greater Than", "10 > 5", "True"),
    ("Less Than or Equal", "5 <= 5", "True"),
    ("Not Equal", "a != 80", "True"),
    # --- if/else 表达式 ---
    ("If/Else (Then branch)", 'if 10 > 5 then "yes" else "no"', "'yes'"),
    ("If/Else (Else branch)", "if a == 99 then 1 else 0", "0"),
    ("If without Else (True)", "if true then 10", "10"),
    ("If without Else (False)", "if false then 10", "None"),
    ("If with Block", "let x = if 1 > 0 { 500 }; x", "500"),
]


def run_lucid_code(source_code, vm_instance):
    """
    一个辅助函数，用于执行完整的 Lucid 代码处理流程。
    现在它接收一个 VM 实例以保持会话状态。
    """
    try:
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        ast = parser.parse()

        compiler = Compiler()
        chunk = compiler.compile(ast)

        result_value = vm_instance.interpret(chunk)
        return result_value

    except Exception as e:
        import traceback

        return f"ERROR: {e}\n{traceback.format_exc()}"


def main():
    print("=" * 40)
    print(" R U N N I N G   L U C I D   T E S T S ")
    print("=" * 40)

    passed = 0
    failed = 0

    # 为整个测试过程创建一个独立的VM实例
    vm = VM()

    for i, (desc, code, expected_repr) in enumerate(TEST_CASES):
        print(f"[{i+1:02d}] Running test: {desc:<25}", end="")

        actual_result = run_lucid_code(code, vm)
        actual_repr = repr(actual_result)

        if actual_repr == expected_repr:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            print(f"      Code:     {code}")
            print(f"      Expected: {expected_repr}")
            print(f"      Got:      {actual_repr}")
            failed += 1

    print("-" * 40)
    print(f"Result: {passed} passed, {failed} failed.")
    print("=" * 40)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
