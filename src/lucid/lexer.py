# src/lucid/lexer.py
import re
from .core_types import Token


class Lexer:
    """词法分析器 (v3.0 - 最终稳定版)"""

    def __init__(self, text):
        self.text = text
        self.token_specs = [
            ("SKIP", r"[ \t\r\n\u00A0]+"),
            ("STRING", r'"[^"]*"'),
            ("INTEGER", r"\d+"),
            ("FN", r"\bfn\b"),
            ("LET", r"\blet\b"),
            ("TRUE", r"\btrue\b"),
            ("FALSE", r"\bfalse\b"),
            ("IF", r"\bif\b"),
            ("ELSE", r"\belse\b"),
            ("THEN", r"\bthen\b"),
            ("RETURN", r"\breturn\b"),
            ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
            ("PIPE", r"\|>"),
            ("EQ", r"=="),
            ("NE", r"!="),
            ("GTE", r">="),
            ("LTE", r"<="),
            ("GT", r">"),
            ("LT", r"<"),
            ("PLUS", r"\+"),
            ("MINUS", r"-"),
            ("MUL", r"\*"),
            ("DIV", r"/"),
            ("CARET", r"\^"),
            ("EQUALS", r"="),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("LBRACE", r"\{"),
            ("RBRACE", r"\}"),
            ("COMMA", r","),
            ("SEMICOLON", r";"),
        ]
        self.token_regex = "|".join(
            f"(?P<{name}>{pattern})" for name, pattern in self.token_specs
        )

    def get_token_stream(self):
        for match in re.finditer(self.token_regex, self.text):
            type, value = match.lastgroup, match.group()
            if type == "SKIP":
                continue
            if type == "INTEGER":
                value = int(value)
            elif type == "TRUE":
                value = True
            elif type == "FALSE":
                value = False
            elif type == "STRING":
                value = value[1:-1]
            yield Token(type, value)
        yield Token("EOF", None)
