class Node:
    pass


class Program(Node):
    def __init__(self, stmts):
        self.stmts = stmts
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Program({self.stmts})@{getattr(self,'line',None)}"


class Step(Node):
    def __init__(self, name):
        self.name = name
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Step({self.name})@{getattr(self,'line',None)}"


class Goto(Node):
    def __init__(self, target):
        self.target = target
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Goto({self.target})@{getattr(self,'line',None)}"


class Print(Node):
    def __init__(self, expr):
        self.expr = expr
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Print({self.expr})@{getattr(self,'line',None)}"


class Repeat(Node):
    def __init__(self, count, block):
        self.count = count
        self.block = block
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Repeat({self.count},{self.block})@{getattr(self,'line',None)}"


class If(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block
        self.line = None
        self.col = None

    def __repr__(self):
        return f"If({self.cond},{self.block})@{getattr(self,'line',None)}"


class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Assign({self.name},{self.expr})@{getattr(self,'line',None)}"


class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        self.line = None
        self.col = None

    def __repr__(self):
        return f"BinOp({self.op},{self.left},{self.right})@{getattr(self,'line',None)}"


class Number(Node):
    def __init__(self, value):
        self.value = value
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Number({self.value})@{getattr(self,'line',None)}"


class String(Node):
    def __init__(self, value):
        self.value = value
        self.line = None
        self.col = None

    def __repr__(self):
        return f"String({self.value!r})@{getattr(self,'line',None)}"


class Var(Node):
    def __init__(self, name):
        self.name = name
        self.line = None
        self.col = None

    def __repr__(self):
        return f"Var({self.name})@{getattr(self,'line',None)}"
