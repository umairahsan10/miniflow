import re, sys
TOKEN_SPEC = [
    ('NUMBER',   r'\d+'),
    ('STRING',   r'"([^"\\]|\\.)*"'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('EQ',       r'=='),
    ('NE',       r'!='),
    ('LE',       r'<='),
    ('GE',       r'>='),
    ('LT',       r'<'),
    ('GT',       r'>'),
    ('ASSIGN',   r'='),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('TIMES',    r'\*'),
    ('DIV',      r'\/'),
    ('LP',       r'\{'),
    ('RP',       r'\}'),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t]+'),
    ('COMMENT',  r'\#.*'),
    ('MISMATCH', r'.'),
]
KEYWORDS = {'step','goto','print','repeat','times','if','then','and','or','not'}
tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)
get_token = re.compile(tok_regex).match

class Token:
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
    def __repr__(self):
        return f'Token({self.type},{self.value!r},{self.line},{self.col})'

def tokenize(code):
    mo = get_token(code)
    index = 0
    tokens = []
    cur_line = 1
    cur_col = 1
    while mo is not None:
        typ = mo.lastgroup
        val = mo.group(typ)
        if typ == 'NEWLINE':
            tokens.append(Token('NEWLINE','\n',cur_line,cur_col))
            cur_line += 1
            cur_col = 1
        elif typ == 'SKIP' or typ == 'COMMENT':
            pass
        elif typ == 'MISMATCH':
            raise SyntaxError(f'Unexpected character {val!r} at line {cur_line} col {cur_col}')
        else:
            if typ == 'ID' and val in KEYWORDS:
                typ = val.upper()
            tokens.append(Token(typ,val,cur_line,cur_col))
            cur_col += len(val)
        index = mo.end()
        mo = get_token(code, index)
    tokens.append(Token('EOF','',cur_line,cur_col))
    return tokens

if __name__=='__main__':
    import sys
    code = open(sys.argv[1]).read()
    for t in tokenize(code):
        print(t)
