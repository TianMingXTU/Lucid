# src/lucid/parser.py
from .core_types import Token
from .ast import *


class Parser:
    """语法分析器 (v3.1 - 最终稳定版)"""

    def __init__(self, lexer):
        self.tokens = lexer.get_token_stream()
        self.current_token = next(self.tokens)

    def _eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = next(self.tokens)
        else:
            raise SyntaxError(
                f"Parser Error: Expected {token_type}, but found {self.current_token.type}"
            )

    def _primary(self):
        """处理原子表达式，这是语法的最高优先级部分"""
        token = self.current_token
        if token.type == "INTEGER":
            self._eat("INTEGER")
            return Num(token)
        elif token.type == "IDENTIFIER":
            # This logic needs to be careful about function calls vs variables.
            # A more robust implementation might use a different approach.
            node = VarAccess(token)
            self._eat("IDENTIFIER")
            if self.current_token.type == "LPAREN":
                return self._call(node)
            return node
        elif token.type in ("TRUE", "FALSE"):
            self._eat(token.type)
            return Boolean(token)
        elif token.type == "STRING":
            self._eat("STRING")
            return StringLiteral(token)
        elif token.type == "LPAREN":
            self._eat("LPAREN")
            node = self._expression()
            self._eat("RPAREN")
            return node
        elif token.type == "FN":
            return self._function()
        elif token.type == "IF":
            return self._if()
        # *** FIX: Allow a block statement to be a primary expression ***
        elif token.type == "LBRACE":
            return self._block()

        raise SyntaxError(f"Invalid primary expression at {token}")

    def _call(self, node):
        args = []
        self._eat("LPAREN")
        if self.current_token.type != "RPAREN":
            args.append(self._expression())
            while self.current_token.type == "COMMA":
                self._eat("COMMA")
                args.append(self._expression())
        self._eat("RPAREN")

        # Check for another function call, e.g. foo(1)(2)
        if self.current_token.type == "LPAREN":
            return self._call(CallExpression(node, args))

        return CallExpression(node, args)

    def _unary(self):
        token = self.current_token
        if token.type in ("PLUS", "MINUS"):
            self._eat(token.type)
            return UnaryOp(token, self._unary())

        # This will now correctly handle function calls like `my_func()`
        # because _primary handles it.
        node = self._primary()

        # Handle post-primary function calls like `1.my_method()` if we add them later
        # For now, just handle standard calls.
        if self.current_token.type == "LPAREN":
            # This handles cases like `(fn(){...})()`
            if isinstance(node, FunctionLiteral):
                return self._call(node)

        return node

    def _power(self):
        # *** FIX: Correct implementation for right-associativity ***
        node = self._unary()
        if self.current_token.type == "CARET":
            op = self.current_token
            self._eat("CARET")
            # The right-hand side is parsed with a lower precedence to handle right-associativity
            right = self._power()
            return BinOp(node, op, right)
        return node

    def _factor(self):
        node = self._power()
        while self.current_token.type in ("MUL", "DIV"):
            op = self.current_token
            self._eat(op.type)
            node = BinOp(node, op, self._power())
        return node

    def _term(self):
        node = self._factor()
        while self.current_token.type in ("PLUS", "MINUS"):
            op = self.current_token
            self._eat(op.type)
            node = BinOp(node, op, self._factor())
        return node

    def _comparison(self):
        node = self._term()
        while self.current_token.type in ("GT", "GTE", "LT", "LTE"):
            op = self.current_token
            self._eat(op.type)
            node = BinOp(node, op, self._term())
        return node

    def _equality(self):
        node = self._comparison()
        while self.current_token.type in ("EQ", "NE"):
            op = self.current_token
            self._eat(op.type)
            node = BinOp(node, op, self._comparison())
        return node

    def _expression(self):
        return self._equality()

    def _block(self):
        self._eat("LBRACE")
        block = BlockStatement()
        while self.current_token.type != "RBRACE":
            block.statements.append(self._statement())
        self._eat("RBRACE")
        return block

    def _function(self):
        self._eat("FN")
        self._eat("LPAREN")
        params = []
        if self.current_token.type != "RPAREN":
            token = self.current_token
            self._eat("IDENTIFIER")
            params.append(token)
            while self.current_token.type == "COMMA":
                self._eat("COMMA")
                token = self.current_token
                self._eat("IDENTIFIER")
                params.append(token)
        self._eat("RPAREN")
        body = self._block()
        return FunctionLiteral(params, body)

    def _if(self):
        self._eat("IF")
        condition = self._expression()
        self._eat("THEN")
        then_branch = self._expression()
        else_branch = None
        if self.current_token.type == "ELSE":
            self._eat("ELSE")
            else_branch = self._expression()
        return IfExpression(condition, then_branch, else_branch)

    def _statement(self):
        token = self.current_token
        if token.type == "LET":
            self._eat("LET")
            var_token = self.current_token
            self._eat("IDENTIFIER")
            self._eat("EQUALS")
            value = self._expression()
            node = VarAssign(var_token, value)
        elif token.type == "RETURN":
            self._eat("RETURN")
            value = self._expression()
            node = ReturnStatement(value)
        else:
            node = self._expression()

        if self.current_token.type == "SEMICOLON":
            self._eat("SEMICOLON")
        return node

    def parse(self):
        program_node = BlockStatement()
        while self.current_token.type != "EOF":
            program_node.statements.append(self._statement())
        return program_node
