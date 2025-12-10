from ir import TACInstr
import sys
def run_tac(code):
    env = {}  # variables and temps
    output = []
    labels = {}
    # first pass: find labels
    pc=0
    while pc < len(code):
        instr = code[pc]
        if instr.op=='label':
            labels[instr.a]=pc
        pc+=1
    pc=0
    while pc < len(code):
        instr = code[pc]
        op = instr.op
        if op=='label':
            pc+=1; continue
        if op=='goto':
            target = instr.a
            if target in labels:
                pc = labels[target]+1
                continue
            else:
                raise RuntimeError(f'Unknown label {target}')
        if op=='print':
            val = resolve(instr.a, env)
            output.append(str(val))
            pc+=1; continue
        if op=='assign':
            name = instr.a
            val = resolve(instr.b, env)
            env[name]=val
            pc+=1; continue
        if op=='binop':
            dest = instr.a
            expr = instr.b  # like "a + b" or temps
            parts = expr.split()
            if len(parts)==3:
                left = resolve(parts[0], env)
                oper = parts[1]
                right = resolve(parts[2], env)
                res = eval_binop(left, oper, right)
                env[dest]=res
            else:
                env[dest]=expr
            pc+=1; continue
        if op=='if_gt':
            left = resolve(instr.a, env)
            comp = int(instr.b)
            target = instr.c
            if int(left) > comp:
                if isinstance(target, str) and target.startswith('goto '):
                    lab = target.split()[1]
                    if lab in labels:
                        pc = labels[lab]+1; continue
            pc+=1; continue
        if op=='if_false':
            cond = resolve(instr.a, env)
            skiplabel = instr.b
            if not bool(cond):
                if skiplabel in labels:
                    pc = labels[skiplabel]+1; continue
            pc+=1; continue
        pc+=1
    return output

def resolve(x, env):
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        if x.startswith('"') and x.endswith('"'):
            return x[1:-1]
        if x.isdigit() or (x.startswith('-') and x[1:].isdigit()):
            return int(x)
        return env.get(x, 0)
    return x

def eval_binop(a, op, b):
    if op=='+': return int(a)+int(b)
    if op=='-': return int(a)-int(b)
    if op=='*': return int(a)*int(b)
    if op=='/': return int(a)//int(b) if int(b)!=0 else 0
    if op=='==': return a==b
    if op=='!=': return a!=b
    if op=='>': return int(a)>int(b)
    if op=='<': return int(a)<int(b)
    if op=='>=': return int(a)>=int(b)
    if op=='<=': return int(a)<=int(b)
    if op=='and': return bool(a) and bool(b)
    if op=='or': return bool(a) or bool(b)
    return 0

if __name__=='__main__':
    pass
