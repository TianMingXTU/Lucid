# src/lucid/__main__.py
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler
from .vm import VM, VMResult
from .debug import disassemble_chunk  # 导入我们的新工具

# 添加一个调试开关
DEBUG = True


def main():
    # ...
    print("Lucid Language v4.0 - Now powered by a Bytecode VM!")
    print("Enter 'exit' to quit.")

    compiler = Compiler()
    vm = VM()

    while True:
        try:
            text = input("lucid> ")
            if text.strip().lower() == "exit":
                break
            if not text.strip():
                continue

            lexer = Lexer(text)
            parser = Parser(lexer)
            ast = parser.parse()

            chunk = compiler.compile(ast)

            if not chunk:
                print("Compile Error.")
                continue

            if DEBUG:
                disassemble_chunk(chunk, "Debug Chunk")

            result = vm.interpret(chunk)

        except (
            SyntaxError,
            NameError,
            ZeroDivisionError,
            TypeError,
            NotImplementedError,
        ) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
