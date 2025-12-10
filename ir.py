# Generate simple three-address code (TAC) from AST
from ast import *


class TACInstr:
    def __init__(self, op, a=None, b=None, c=None):
        self.op = op
        self.a = a
        self.b = b
        self.c = c
        self.src = None

    def __repr__(self):
        parts = [self.op]
        for x in (self.a, self.b, self.c):
            if x is not None:
                parts.append(str(x))
        s = " ".join(parts)
        if self.src:
            line, col = self.src
            s = f"{s}  # @{line}:{col}"
        return s

    def simple(self):
        # compact representation without source comments
        parts = [self.op]
        for x in (self.a, self.b, self.c):
            if x is not None:
                parts.append(str(x))
        return " ".join(parts)


class IRGen:
    def __init__(self):
        self.temp_count = 0
        self.code = []

    def newtemp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def emit(self, instr):
        self.code.append(instr)

    def generate(self, prog):
        for s in prog.stmts:
            self.gen_stmt(s)
        return self.code

    def gen_stmt(self, stmt):
        if isinstance(stmt, Step):
            instr = TACInstr("label", stmt.name)
            self.emit(instr)
            instr.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
        elif isinstance(stmt, Goto):
            instr = TACInstr("goto", stmt.target)
            self.emit(instr)
            instr.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
        elif isinstance(stmt, Print):
            t = self.gen_expr(stmt.expr)
            instr = TACInstr("print", t)
            self.emit(instr)
            instr.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
        elif isinstance(stmt, Assign):
            t = self.gen_expr(stmt.expr)
            instr = TACInstr("assign", stmt.name, t)
            self.emit(instr)
            instr.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
        elif isinstance(stmt, Repeat):
            start = f"L{len(self.code)}_{self.temp_count}"
            end = f"END{len(self.code)}_{self.temp_count}"
            counter = self.newtemp()
            instr1 = TACInstr("assign", counter, stmt.count)
            instr1.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
            self.emit(instr1)
            instr2 = TACInstr("label", start)
            instr2.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
            self.emit(instr2)
            for s in stmt.block:
                self.gen_stmt(s)
            # decrement the loop counter using a proper binop so optimizer/runtime can evaluate it
            instr3 = TACInstr("binop", counter, f"{counter} - 1")
            instr3.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
            self.emit(instr3)
            instr4 = TACInstr("if_gt", counter, "0", f"goto {start}")
            instr4.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
            self.emit(instr4)
        elif isinstance(stmt, If):
            t = self.gen_expr(stmt.cond)
            skip = f"END_IF{len(self.code)}_{self.temp_count}"
            instr = TACInstr("if_false", t, skip)
            instr.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
            self.emit(instr)
            for s in stmt.block:
                self.gen_stmt(s)
            instr2 = TACInstr("label", skip)
            instr2.src = (getattr(stmt, "line", None), getattr(stmt, "col", None))
            self.emit(instr2)

    def gen_expr(self, expr):
        if isinstance(expr, Number):
            return expr.value
        if isinstance(expr, String):
            return f'"{expr.value}"'
        if isinstance(expr, Var):
            return expr.name
        if isinstance(expr, BinOp):
            a = self.gen_expr(expr.left)
            b = self.gen_expr(expr.right)
            t = self.newtemp()
            op = expr.op
            opmap = {
                "PLUS": "+",
                "MINUS": "-",
                "TIMES": "*",
                "DIV": "/",
                "EQ": "==",
                "NE": "!=",
                "LT": "<",
                "GT": ">",
                "LE": "<=",
                "GE": ">=",
                "AND": "and",
                "OR": "or",
            }
            sym = opmap.get(op, op)
            instr = TACInstr("binop", t, f"{a} {sym} {b}")
            instr.src = (getattr(expr, "line", None), getattr(expr, "col", None))
            self.emit(instr)
            return t
