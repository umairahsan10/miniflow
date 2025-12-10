# MiniFlow Compiler

## Overview
MiniFlow is a tiny workflow scripting language designed for CS4031 Compiler Construction course project. It supports:

- Step definitions (`step <name>`)
- Conditional execution (`if <condition> then { ... }`)
- Loops (`repeat <number> times { ... }`)
- Goto statements (`goto <step>`)
- Printing (`print <expr>`)
- Integer variables and string literals for print
- Arithmetic, comparison, and logical operators

## Folder Structure
- `lexer.py`       : Tokenizer for MiniFlow
- `parser.py`      : Grammar & parser
- `ast.py`         : AST node definitions
- `semantic.py`    : Symbol table & type checking
- `ir.py`          : Intermediate representation / three-address code
- `optimizer.py`   : Basic optimization (constant folding, dead code elimination)
- `codegen.py`     : Interpreter / execution of TAC
- `main.py`        : Command-line interface to run `.mf` files
- `demos/`         : Demo MiniFlow programs

## Usage
1. Place your `.mf` MiniFlow program in the `demos` folder.
2. Run the compiler:

## Group Members:
1. Umair Ahsan [22K-4275]
2. Muhammad Aliyan Malik [22K-4132]
3. Muhammad Saad [22K-4407]

### Section: BSCS-7A

### Course: Compiler Construction

### Teacher: Faisal Ali