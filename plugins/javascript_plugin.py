import esprima
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

def parse_javascript(code: str) -> esprima.nodes.Program:
    return esprima.parseScript(code)

def analyze_javascript(node: esprima.nodes.Node) -> Dict[str, Any]:
    context = {
        'imports': [],
        'functions': [],
        'classes': [],
    }
    for child in node.body:
        if isinstance(child, esprima.nodes.ImportDeclaration):
            context['imports'].extend(spec.local.name for spec in child.specifiers)
        elif isinstance(child, esprima.nodes.FunctionDeclaration):
            context['functions'].append(child.id.name)
        elif isinstance(child, esprima.nodes.ClassDeclaration):
            context['classes'].append(child.id.name)
    return context

def generate_javascript_comments(generator, node: esprima.nodes.Program, code: str) -> Dict[int, str]:
    comments = {}
    for child in node.body:
        if isinstance(child, (esprima.nodes.FunctionDeclaration, esprima.nodes.ClassDeclaration)):
            line_number = child.location.start.line
            code_snippet = esprima.generate(child)
            context = generator._get_context(child)
            comment = generator._generate_comment_for_snippet(code_snippet, type(child).__name__, context)
            comments[line_number] = comment
    return comments

def format_javascript_comment(comment: str, indent: int, style: str) -> List[str]:
    if style == "jsdoc":
        return [f'{" " * indent}/**'] + [f"{' ' * indent} * {line}" for line in comment.split('\n')] + [f'{" " * indent} */']
    else:  # default to single-line comments
        return [f"{' ' * indent}// {line}" for line in comment.split('\n')]

LANGUAGE_PLUGIN = LanguagePlugin(
    name="javascript",
    file_extensions=[".js"],
    parse_function=parse_javascript,
    analyze_function=analyze_javascript,
    generate_comment_function=generate_javascript_comments,
    format_comment_function=format_javascript_comment
)
