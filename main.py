import sys
from lexer import tokenize
from parser import parse_code
from semantic import check_program, SemanticError
from ir import IRGen
from optimizer import constant_folding, dead_code_elim
from codegen import run_tac
from ast import *


def compile_and_run(code):
    prog = parse_code(code)
    st, diagnostics = check_program(prog)
    irgen = IRGen()
    tac = irgen.generate(prog)
    # optimization
    tac2 = constant_folding(tac)
    tac3, removed = dead_code_elim(tac2)
    out = run_tac(tac3)
    return out, tac, tac3, st, diagnostics, removed, prog


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py file.mf")
        sys.exit(1)
    code = open(sys.argv[1]).read()
    out, tac, tacopt, st, diagnostics, removed, prog = compile_and_run(code)
    print("=== OUTPUT ===")
    for line in out:
        print(line)
    print()
    print("=== TAC ===")
    for t in tac:
        # simple one-line TAC for readability
        try:
            print(t.simple())
        except Exception:
            print(t)
    print()
    print("=== OPT TAC ===")
    for t in tacopt:
        try:
            print(t.simple())
        except Exception:
            print(t)
    print()
    print("=== SYMBOL TABLE ===")
    for k, v in st.items():
        print(f"{k} : {v}")
    print()
    # diagnostics (already collected during check)
    print("=== DIAGNOSTICS ===")
    if diagnostics:
        for d in diagnostics:
            print("ERROR:", d)
    else:
        print("(no errors)")
    print()

    # DCE report
    print("=== DCE REMOVED ===")
    if removed:
        print(f"{len(removed)} instruction(s) removed")
        for r in removed:
            try:
                print(" -", r.simple())
            except Exception:
                print(" -", r)
    else:
        print("(no instructions removed)")
    print()

    # Code structure printout
    print("=== CODE ===")

    def format_node(n, indent=0):
        pad = "  " * indent
        if isinstance(n, Program):
            s = pad + f"Program"
            for x in n.stmts:
                s += "\n" + format_node(x, indent + 1)
            return s
        if isinstance(n, Step):
            return pad + f"Step {n.name} (@{n.line}:{n.col})"
        if isinstance(n, Goto):
            return pad + f"Goto {n.target} (@{n.line}:{n.col})"
        if isinstance(n, Print):
            return pad + f"Print: " + format_node(n.expr, indent + 1)
        if isinstance(n, Repeat):
            s = pad + f"Repeat {n.count} (@{n.line}:{n.col})"
            for x in n.block:
                s += "\n" + format_node(x, indent + 1)
            return s
        if isinstance(n, If):
            s = pad + f"If (@{n.line}:{n.col}) Cond: " + format_node(n.cond, 0)
            for x in n.block:
                s += "\n" + format_node(x, indent + 1)
            return s
        if isinstance(n, Assign):
            return (
                pad
                + f"Assign {n.name} = "
                + format_node(n.expr, 0)
                + f" (@{n.line}:{n.col})"
            )
        if isinstance(n, BinOp):
            return (
                pad
                + f"BinOp {n.op} (@{n.line}:{n.col})\n"
                + format_node(n.left, indent + 1)
                + "\n"
                + format_node(n.right, indent + 1)
            )
        if isinstance(n, Number):
            return pad + f"Number {n.value} (@{n.line}:{n.col})"
        if isinstance(n, String):
            return pad + f"String {n.value!r} (@{n.line}:{n.col})"
        if isinstance(n, Var):
            return pad + f"Var {n.name} (@{n.line}:{n.col})"
        return pad + repr(n)

    if prog:
        # very simple AST: one readable line per statement, indented for blocks
        def expr_repr(e):
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
            if isinstance(e, Number):
                return str(e.value)
            if isinstance(e, String):
                return f'"{e.value}"'
            if isinstance(e, Var):
                return e.name
            if isinstance(e, BinOp):
                left = expr_repr(e.left)
                right = expr_repr(e.right)
                sym = opmap.get(e.op, e.op)
                return f"{left} {sym} {right}"
            return repr(e)

        def simple_ast(n, indent=0):
            pad = "  " * indent
            if isinstance(n, Program):
                lines = []
                for s in n.stmts:
                    lines.append(simple_ast(s, indent))
                return "\n".join(lines)
            if isinstance(n, Step):
                return pad + f"Step {n.name}"
            if isinstance(n, Goto):
                return pad + f"Goto {n.target}"
            if isinstance(n, Print):
                return pad + f"Print {expr_repr(n.expr)}"
            if isinstance(n, Assign):
                return pad + f"{n.name} = {expr_repr(n.expr)}"
            if isinstance(n, Repeat):
                lines = [pad + f"Repeat {n.count} times"]
                for s in n.block:
                    lines.append(simple_ast(s, indent + 1))
                return "\n".join(lines)
            if isinstance(n, If):
                lines = [pad + f"If {expr_repr(n.cond)}"]
                for s in n.block:
                    lines.append(simple_ast(s, indent + 1))
                return "\n".join(lines)
            return pad + repr(n)

        print(simple_ast(prog))
    else:
        print("(no AST)")
    print()
    print()
