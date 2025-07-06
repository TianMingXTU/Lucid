# src/lucid/ast.py


class ASTNode:
    pass


# ... (BinOp, UnaryOp, Num, Boolean, StringLiteral, IfExpression 等保持不变) ...
class BinOp(ASTNode):
    def __init__(self, left, op_token, right):
        self.left, self.op, self.right = left, op_token, right


class UnaryOp(ASTNode):
    def __init__(self, op_token, expr):
        self.op, self.expr = op_token, expr


class Num(ASTNode):
    def __init__(self, token):
        self.token, self.value = token, token.value


class Boolean(ASTNode):
    def __init__(self, token):
        self.token, self.value = token, token.value


class StringLiteral(ASTNode):
    def __init__(self, token):
        self.token, self.value = token, token.value


# *** NEW: Unit Number Node ***
class UnitNumber(ASTNode):
    def __init__(self, number_token, unit_token):
        self.token = number_token
        self.value = number_token.value
        self.unit_token = unit_token
        self.unit = unit_token.value


class IfExpression(ASTNode):
    def __init__(self, condition, then_branch, else_branch):
        self.condition, self.then_branch, self.else_branch = (
            condition,
            then_branch,
            else_branch,
        )


class VarAssign(ASTNode):
    def __init__(self, var_token, value_node):
        self.var_token, self.var_name, self.value_node = (
            var_token,
            var_token.value,
            value_node,
        )


class VarAccess(ASTNode):
    def __init__(self, var_token):
        self.var_token, self.var_name = var_token, var_token.value


class BlockStatement(ASTNode):
    def __init__(self):
        self.statements = []


class FunctionLiteral(ASTNode):
    def __init__(self, parameters, body):
        self.parameters, self.body = parameters, body


class CallExpression(ASTNode):
    def __init__(self, function, arguments):
        self.function, self.arguments = function, arguments


class ReturnStatement(ASTNode):
    def __init__(self, return_value):
        self.return_value = return_value
