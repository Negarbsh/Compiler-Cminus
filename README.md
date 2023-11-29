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

## Project Structure

- `.gitignore`: Specifies files to be ignored in Git version control.
- `code_generator.py`: Handles the generation of intermediate code from the parsed input.
- `compiler.py`: The main driver of the compilation process, coordinating various components.
- `data.json`: Contains necessary data or configuration used by the compiler.
- `heap_manager.py`: Manages dynamic memory allocation during the compilation.
- `Parser.py`: Parses the tokens into a syntax tree based on the defined grammar.
- `README.md`: Provides an overview and documentation for the project.
- `rules.txt`: Contains grammar and syntax rules for C-minus language.
- `scanner.py`: Lexical analyzer that converts input code into tokens.
- `symbol_table.py`: Manages a symbol table, tracking variable and function declarations.

## Usage

To use the compiler, run `compiler.py` with a C-minus source file as input. The program will process the input and generate an output in the form of an intermediate representation or error messages if any issues are detected in the source code.

## Maintainers

- [Negar Babashah](https://github.com/Negarbsh)
- [Hasti Karimi](https://github.com/HastiKarimi)