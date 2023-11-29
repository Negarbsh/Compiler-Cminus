from scanner import Scanner
from parserr import Parser
from symbol_table import SymbolTable
from heap_manager import HeapManager
from code_generator import CodeGenerator

# initialize a scanner and call get_next_token repeatedly

list_needed_files = ["output", "input", "semantic_errors"]


def create_file_by_mode(name, mode, encoding='utf-8'):
    name_pure = name.split(".")[0]
    if name_pure in list_needed_files:
        return open(name, mode, encoding=encoding)
    return DummyFile()


class DummyFile:
    def __init__(self):
        pass

    def write(self, text):
        pass

    def close(self):
        pass


in_file = create_file_by_mode("input.txt", "r")
out_file = create_file_by_mode("tokens.txt", "w+")
lex_file = create_file_by_mode("lexical_errors.txt", "w+")
sym_file = create_file_by_mode("symbol_table.txt", "w+")
parser_errors_file = create_file_by_mode("syntax_errors.txt", "w+")
parser_tree_file = create_file_by_mode("parse_tree.txt", "w+", encoding='utf-8')
generated_code_file = create_file_by_mode("output.txt", "w+")
semantic_errors_file = create_file_by_mode("semantic_errors.txt", "w+")

# in_file = open("input.txt", "r")
# out_file = open("tokens.txt", "w+")
# lex_file = open("lexical_errors.txt", "w+")
# sym_file = open("symbol_table.txt", "w+")
# parser_errors_file = open("syntax_errors.txt", "w+")
# parser_tree_file = open("parse_tree.txt", "w+", encoding='utf-8')
# generated_code_file = open("output.txt", "w+")

heap = HeapManager()
symbol_table = SymbolTable(heap)

scanner = Scanner(
    input_file=in_file,
    output_file=out_file,
    lex_file=lex_file,
    sym_file=sym_file,
    symbol_table=symbol_table
)

code_generator = CodeGenerator(symbol_table=symbol_table, heap=heap)

parser = Parser(errors_file=parser_errors_file, parse_tree_file=parser_tree_file,
                scanner=scanner, code_gen=code_generator)
parser.run()

code_generator.write_pb_to_file(generated_code_file, semantic_errors_file)

in_file.close()
out_file.close()
lex_file.close()
sym_file.close()
parser_errors_file.close()
semantic_errors_file.close()
generated_code_file.close()