import pycparser
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class LanguagePlugin:
    name: str
    file_extensions: List[str]
    parse_function: callable
    analyze_function: callable
    generate_comment_function: callable
    format_comment_function: callable

def parse_cpp(code: str) -> pycparser.c_ast.FileAST:
    return pycparser.c_parser.CParser().parse(code)

def analyze_cpp(node: pycparser.c_ast.FileAST) -> Dict[str, Any]:
    context = {
        'includes': [],
        'functions': [],
        'structs': [],
    }
    for child in node.ext:
        if isinstance(child, pycparser.c_ast.FuncDef):
            context['functions'].append(child.decl.name)
        elif isinstance(child, pycparser.c_ast.Typedef) and isinstance(child.type, pycparser.c_ast.Struct):
            context['structs'].append(child.name)
        elif isinstance(child, pycparser.c_ast.Include):
            context['includes'].append(child.name)
    return context

def generate_cpp_comments(generator, node: pycparser.c_ast.FileAST, code: str) -> Dict[int, str]:
    comments = {}
    for child in node.ext:
        if isinstance(child, (pycparser.c_ast.FuncDef, pycparser.c_ast.Typedef)):
            line_number = child.coord.line
            code_snippet = pycparser.c_generator.CGenerator().visit(child)
            context = generator._get_context(child)
            comment = generator._generate_comment_for_snippet(code_snippet, type(child).__name__, context)
            comments[line_number] = comment
    return comments

def format_cpp_comment(comment: str, indent: int, style: str) -> List[str]:
    if style == "doxygen":
        return [f'{" " * indent}/**'] + [f"{' ' * indent} * {line}" for line in comment.split('\n')] + [f'{" " * indent} */']
    else:  # default to single-line comments
        return [f"{' ' * indent}// {line}" for line in comment.split('\n')]

LANGUAGE_PLUGIN = LanguagePlugin(
    name="cpp",
    file_extensions=[".cpp", ".h"],
    parse_function=parse_cpp,
    analyze_function=analyze_cpp,
    generate_comment_function=generate_cpp_comments,
    format_comment_function=format_cpp_comment
)
