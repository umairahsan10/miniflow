from ir import TACInstr


def constant_folding(code):
    new = []
    for instr in code:
        if instr.op == "binop" and isinstance(instr.b, str):
            parts = instr.b.split()
            try:
                a = int(parts[0])
                op = parts[1]
                b = int(parts[2])
                if op == "+":
                    res = a + b
                elif op == "-":
                    res = a - b
                elif op == "*":
                    res = a * b
                elif op == "/":
                    res = a // b if b != 0 else a // 1
                else:
                    new.append(instr)
                    continue
                new.append(TACInstr("assign", instr.a, res))
            except Exception:
                new.append(instr)
        else:
            new.append(instr)
    return new


def dead_code_elim(code):
    # very naive: remove assignments to temps that are never used
    used = set()
    for instr in code:
        for part in (instr.a, instr.b, instr.c):
            if isinstance(part, str) and part.startswith("t"):
                used.add(part)
    new = []
    removed = []
    for instr in code:
        if (
            instr.op == "assign"
            and isinstance(instr.a, str)
            and instr.a.startswith("t")
            and instr.a not in used
        ):
            removed.append(instr)
            continue
        new.append(instr)
    return new, removed
