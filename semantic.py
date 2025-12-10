from ast import *


class SemanticError(Exception):
    pass


class SymbolTable:
    def __init__(self):
        self.table = {}

    def declare(self, name, typ):
        if name in self.table:
            self.table[name] = typ
        else:
            self.table[name] = typ

    def lookup(self, name):
        return self.table.get(name, None)

    def items(self):
        return self.table.items()


def check_program(prog):
    st = SymbolTable()
    diagnostics = []
    # first pass: collect step names and variable declarations from assignments
    for s in prog.stmts:
        collect_decls(s, st)
    # second pass: type check (collect errors rather than raising)
    for s in prog.stmts:
        try:
            type_check_stmt(s, st)
        except SemanticError as e:
            diagnostics.append(str(e))
    return st, diagnostics


def collect_decls(stmt, st):
    if isinstance(stmt, Step):
        st.declare(stmt.name, "step")
    elif isinstance(stmt, Assign):
        st.declare(stmt.name, "int")
    elif isinstance(stmt, Repeat):
        for x in stmt.block:
            collect_decls(x, st)
    elif isinstance(stmt, If):
        for x in stmt.block:
            collect_decls(x, st)
    # other statements don't declare


def type_check_stmt(stmt, st):
    if isinstance(stmt, Step):
        return
    if isinstance(stmt, Goto):
        if st.lookup(stmt.target) != "step":
            raise SemanticError(f"Undefined step {stmt.target}")
    if isinstance(stmt, Print):
        type_of_expr(stmt.expr, st)
    if isinstance(stmt, Assign):
        t = type_of_expr(stmt.expr, st)
        if t != "int" and t != "string":
            raise SemanticError(f"Cannot assign type {t} to variable {stmt.name}")
    if isinstance(stmt, Repeat):
        # count must be number
        if not isinstance(stmt.count, int):
            raise SemanticError("Repeat count must be integer literal")
        for x in stmt.block:
            type_check_stmt(x, st)
    if isinstance(stmt, If):
        t = type_of_condition(stmt.cond, st)
        if t != "bool":
            raise SemanticError("If condition must be boolean")
        for x in stmt.block:
            type_check_stmt(x, st)


def type_of_expr(expr, st):
    if isinstance(expr, Number):
        return "int"
    if isinstance(expr, String):
        return "string"
    if isinstance(expr, Var):
        t = st.lookup(expr.name)
        if t is None:
            raise SemanticError(f"Undefined variable {expr.name}")
        return t
    if isinstance(expr, BinOp):
        left = type_of_expr(expr.left, st)
        right = type_of_expr(expr.right, st)
        if expr.op in ("PLUS", "MINUS", "TIMES", "DIV"):
            if left == "int" and right == "int":
                return "int"
            else:
                raise SemanticError("Arithmetic on non-int")
        if expr.op in ("EQ", "NE", "LT", "GT", "LE", "GE"):
            return "bool"
        if expr.op in ("AND", "OR"):
            return "bool"
    raise SemanticError("Unknown expression type")


def type_of_condition(cond, st):
    # condition is BinOp possibly chained; reuse type_of_expr
    t = type_of_expr(cond, st)
    if t == "bool":
        return "bool"
    return "bool"
