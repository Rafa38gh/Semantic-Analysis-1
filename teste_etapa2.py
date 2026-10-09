from Lexer import Lexer
from parser import Parser
from name_resolver import resolve_names
from semantic_errors import SemanticError

fonte = """
int f(int a, bool b) { return 0; }
int f() { return 1; }
int main() { return 0; }
"""

program = Parser(Lexer(fonte).scan()).parse()
try:
    resolve_names(program)
except SemanticError as erro:
    print(erro)

for function in program.functions:
    simbolo = function.metadata["symbol"]
    print(simbolo.name, simbolo.type, simbolo.parameter_types)