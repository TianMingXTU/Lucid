# src/lucid/core_types.py


class Token:
    """
    令牌类，用于存储词法分析中识别出的单元。
    它包含类型、值以及可选的位置信息。
    """

    def __init__(self, type, value, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        """返回令牌的字符串表示形式，方便调试"""
        return f"Token({self.type}, {repr(self.value)})"

    def __repr__(self):
        return self.__str__()
