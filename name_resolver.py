from __future__ import annotations

from ast_nodes import Program, SourceSpan, FunctionDecl, TypeName
from semantic_errors import SemanticDiagnostic, SemanticError, SemanticErrorKind
from symbols import FunctionSymbol, Scope, Symbol, SymbolKind


def declare(scope: Scope, symbol: Symbol) -> bool:
    """Declara um símbolo no escopo.
    Retorna False se o nome já existe no escopo"""
    if symbol.name in scope.symbols:
        return False
    scope.symbols[symbol.name] = symbol
    return True


def lookup(scope: Scope | None, name: str) -> Symbol | None:
    """Procura o nome do escopo mais interno"""
    while scope is not None:
        symbol = scope.symbols.get(name)

        if symbol is not None:
            return symbol
        scope = scope.parent

    return None


def resolve_names(program: Program) -> None:
    """Construa escopos, símbolos e vínculos entre usos e declarações."""

    # 1. Colete todas as assinaturas de função.
    # 2. Valide a existência e a assinatura de main.
    # 3. Percorra os corpos em ordem, criando um escopo para cada bloco.
    # 4. Anote declarações, usos e blocos na AST.
    # 5. Acumule os diagnósticos desta passagem antes de lançar SemanticError.
    NameResolver().resolve_program(program)


class NameResolver:
    def __init__(self) -> None:
        self.diagnostics: list[SemanticDiagnostic] = [] #Lista de erros
        self.functions: dict[str, FunctionSymbol] = {}      # Tabela de funções

    def error(self, kind: SemanticErrorKind, message: str, span: SourceSpan) -> None:
        self.diagnostics.append(SemanticDiagnostic(kind, message, span))

    def resolve_program(self, program: Program) -> None:
        for function in program.functions:
            self.collect_function(function)

        self.check_main(program)
        
        if self.diagnostics:
            raise SemanticError(self.diagnostics)

    def collect_function(self, function: FunctionDecl) -> None:
        symbol = FunctionSymbol(
            name=function.name,
            kind = SymbolKind.FUNCTION,
            type = function.return_type,
            declaration=function,
            parameter_types=tuple(p.type for p in function.parameters),
        )
        function.metadata['symbol'] = symbol

        if function.name in self.functions:
            self.error(SemanticErrorKind.DUPLICATE_FUNCTION, f"Função {function.name} já declarada", function.span)
            return

        self.functions[function.name] = symbol

    def check_main(self, program: Program) -> None:
        main = self.functions.get("main")

        if main is None:
            self.error(SemanticErrorKind.INVALID_MAIN, "programa não declarou 'int main()'", program.span)
            return

        if main.type is not TypeName.INT or main.parameter_types:
           self.error(SemanticErrorKind.INVALID_MAIN, "a assinatura da main deve ser 'int main()'", main.declaration.span)

