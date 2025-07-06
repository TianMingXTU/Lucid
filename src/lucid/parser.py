# src/lucid/parser.py
from .core_types import Token
from .ast import *


class Parser:
    """语法分析器 (v3.3 - 最终稳定版)"""

    def __init__(self, lexer):
        self.tokens = lexer.get_token_stream()
        self.current_token = next(self.tokens)

    def _eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = next(self.tokens)
        else:
            raise SyntaxError(
                f"Parser Error: Expected {token_type}, but found {self.current_token.type} ({self.current_token.value})"
            )

    def _primary(self):
        """处理原子表达式，这是语法的最高优先级部分"""
        token = self.current_token
        if token.type == "INTEGER":
            self._eat("INTEGER")
            return Num(token)
        elif token.type == "IDENTIFIER":
            self._eat("IDENTIFIER")
            return VarAccess(token)
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
        elif token.type == "LBRACE":
            return self._block()
        # *** FIX: Correctly parse spawn as a primary expression ***
        elif token.type == "SPAWN":
            return self._spawn()
        raise SyntaxError(f"Invalid primary expression at {token}")

    def _call(self):
        """处理函数调用"""
        node = self._primary()
        while self.current_token.type == "LPAREN":
            self._eat("LPAREN")
            args = []
            if self.current_token.type != "RPAREN":
                args.append(self._expression())
                while self.current_token.type == "COMMA":
                    self._eat("COMMA")
                    args.append(self._expression())
            self._eat("RPAREN")
            node = CallExpression(node, args)
        return node

    def _unary(self):
        """处理一元运算符，包括 await"""
        token = self.current_token
        if token.type in ("PLUS", "MINUS"):
            self._eat(token.type)
            return UnaryOp(token, self._unary())
        # *** FIX: Correctly parse await as a unary prefix operator ***
        if token.type == "AWAIT":
            self._eat("AWAIT")
            return AwaitExpression(self._unary())
        return self._call()

    def _power(self):
        """处理幂运算 (右结合)"""
        node = self._unary()
        if self.current_token.type == "CARET":
            op = self.current_token
            self._eat("CARET")
            node = BinOp(node, op, self._power())
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

    def _pipe(self):
        node = self._equality()
        while self.current_token.type == "PIPE":
            op = self.current_token
            self._eat("PIPE")
            node = BinOp(node, op, self._equality())
        return node

    def _expression(self):
        return self._pipe()

    def _block(self):
        self._eat("LBRACE")
        block = BlockStatement()
        while self.current_token.type not in ("RBRACE", "EOF"):
            block.statements.append(self._statement())
        self._eat("RBRACE")
        return block

    def _spawn(self):
        self._eat("SPAWN")
        return SpawnExpression(self._block())

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
        if self.current_token.type == "LET":
            self._eat("LET")
            var_token = self.current_token
            self._eat("IDENTIFIER")
            self._eat("EQUALS")
            value = self._expression()
            node = VarAssign(var_token, value)
        elif self.current_token.type == "RETURN":
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
