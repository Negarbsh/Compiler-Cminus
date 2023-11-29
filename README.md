# Compiler-Cminus

**Python3 based one-pass compiler for a simplified C-minus**

## Overview

This project is a Python 3 implementation of a one-pass compiler for a simplified version of the C programming language, called C-minus. The compiler processes C-minus source code and generates an intermediate representation. It's designed to be lightweight and efficient, making it suitable for educational purposes and small-scale projects.

## Features

- **Lexical Analysis:** Uses `scanner.py` to break down the source code into tokens.
- **Syntax Parsing:** Employs `Parser.py` to analyze the program structure based on grammar rules.
- **Symbol Table Management:** Utilizes `symbol_table.py` for tracking identifiers and their attributes throughout the compilation process.
- **Code Generation:** Converts parsed code into an intermediate representation using `code_generator.py`.
- **Heap Management:** Manages memory allocation during runtime using `heap_manager.py`.
- **Error Handling:** Detects and reports syntax and semantic errors.

