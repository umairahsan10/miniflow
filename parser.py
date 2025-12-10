from lexer import tokenize, Token
from ast import *
import sys


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.cur = tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.cur = self.tokens[self.pos]
        else:
            self.cur = Token("EOF", "", self.cur.line, self.cur.col)

    def accept(self, typ):
        if self.cur.type == typ:
            val = self.cur.value
            self.advance()
            return val
        return None

    def expect_token(self, typ):
        # return the Token object (value, line, col) for better source mapping
        if self.cur.type == typ:
            tok = self.cur
            self.advance()
            return tok
        raise ParserError(
            f"Expected {typ} but got {self.cur.type} at line {self.cur.line}"
        )

    def expect(self, typ):
        if self.cur.type == typ:
            val = self.cur.value
            self.advance()
            return val
        raise ParserError(
            f"Expected {typ} but got {self.cur.type} at line {self.cur.line}"
        )

    def parse(self):
        stmts = []
        while self.cur.type != "EOF":
            if self.cur.type == "NEWLINE":
                self.advance()
                continue
            stmt = self.parse_statement()
            stmts.append(stmt)
        return Program(stmts)

    def parse_statement(self):
        if self.cur.type == "STEP":
            return self.parse_step()
        if self.cur.type == "GOTO":
            return self.parse_goto()
        if self.cur.type == "PRINT":
            return self.parse_print()
        if self.cur.type == "REPEAT":
            return self.parse_repeat()
        if self.cur.type == "IF":
            return self.parse_if()
        # assignment? identifier ASSIGN ...
        if self.cur.type == "ID":
            # lookahead
            name = self.cur.value
            self.advance()
            if self.cur.type == "ASSIGN":
                self.advance()
                expr = self.parse_expr()
                return Assign(name, expr)
            else:
                raise ParserError(
                    f"Unexpected token after ID: {self.cur.type} at line {self.cur.line}"
                )
        raise ParserError(f"Unexpected token {self.cur.type} at line {self.cur.line}")

    def parse_step(self):
        self.expect("STEP")
        tok = self.expect_token("ID")
        node = Step(tok.value)
        node.line = tok.line
        node.col = tok.col
        return node

    def parse_goto(self):
        self.expect("GOTO")
        tok = self.expect_token("ID")
        node = Goto(tok.value)
        node.line = tok.line
        node.col = tok.col
        return node

    def parse_print(self):
        self.expect("PRINT")
        expr = self.parse_expr()
        node = Print(expr)
        # use expression position if available
        node.line = getattr(expr, "line", None)
        node.col = getattr(expr, "col", None)
        return node

    def parse_repeat(self):
        self.expect("REPEAT")
        num_tok = self.expect_token("NUMBER")
        num = num_tok.value
        self.expect("TIMES")  # 'times' keyword
        self.expect("LP")  # {
        block = []
        while self.cur.type != "RP":
            if self.cur.type == "NEWLINE":
                self.advance()
                continue
            block.append(self.parse_statement())
        self.expect("RP")
        node = Repeat(int(num), block)
        node.line = num_tok.line
        node.col = num_tok.col
        return node

    def parse_condition(self):
        # For simplicity, reuse parse_expr (which handles comparisons and logical ops)
        return self.parse_expr()

    def parse_if(self):
        self.expect("IF")
        cond = self.parse_condition()
        self.expect("THEN")
        self.expect("LP")
        block = []
        while self.cur.type != "RP":
            if self.cur.type == "NEWLINE":
                self.advance()
                continue
            block.append(self.parse_statement())
        self.expect("RP")
        node = If(cond, block)
        node.line = getattr(cond, "line", None)
        node.col = getattr(cond, "col", None)
        return node

    # expression parsing (simple)
    def parse_expr(self):
        node = self.parse_term()
        while self.cur.type in (
            "PLUS",
            "MINUS",
            "TIMES",
            "DIV",
            "EQ",
            "NE",
            "LT",
            "GT",
            "LE",
            "GE",
            "AND",
            "OR",
        ):
            op_tok = self.cur
            op = op_tok.type
            self.advance()
            right = self.parse_term()
            binnode = BinOp(op, node, right)
            binnode.line = op_tok.line
            binnode.col = op_tok.col
            node = binnode
        return node

    def parse_term(self):
        if self.cur.type == "NUMBER":
            tok = self.expect_token("NUMBER")
            val = int(tok.value)
            node = Number(val)
            node.line = tok.line
            node.col = tok.col
            return node
        if self.cur.type == "STRING":
            tok = self.expect_token("STRING")
            s = tok.value[1:-1]  # strip quotes
            node = String(s)
            node.line = tok.line
            node.col = tok.col
            return node
        if self.cur.type == "ID":
            tok = self.expect_token("ID")
            name = tok.value
            node = Var(name)
            node.line = tok.line
            node.col = tok.col
            return node
        raise ParserError(f"Unexpected term {self.cur.type} at line {self.cur.line}")


def parse_code(code):
    tokens = tokenize(code)
    p = Parser(tokens)
    return p.parse()


if __name__ == "__main__":
    import sys

    code = open(sys.argv[1]).read()
    ast = parse_code(code)
    print(ast)
