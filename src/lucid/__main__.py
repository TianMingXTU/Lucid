# src/lucid/__main__.py
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter


def main():
    """Lucid Language v3.0 - Stable REPL"""
    print("Lucid Language v3.0 - Stable REPL")
    print("Enter 'exit' to quit.")
    interpreter = Interpreter()
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
            result = interpreter.interpret(ast)
            if result is not None:
                print(repr(result))
        except (SyntaxError, NameError, ZeroDivisionError, TypeError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
