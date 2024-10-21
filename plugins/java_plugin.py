import javalang
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

def parse_java(code: str) -> javalang.tree.CompilationUnit:
    return javalang.parse.parse(code)

def analyze_java(node: javalang.tree.CompilationUnit) -> Dict[str, Any]:
    context = {
        'imports': [],
        'methods': [],
        'classes': [],
    }
    for path, child in node.filter(javalang.tree.Import):
        context['imports'].append(child.path)
    for path, child in node.filter(javalang.tree.MethodDeclaration):
        context['methods'].append(child.name)
    for path, child in node.filter(javalang.tree.ClassDeclaration):
        context['classes'].append(child.name)
    return context

def generate_java_comments(generator, node: javalang.tree.CompilationUnit, code: str) -> Dict[int, str]:
    comments = {}
    for path, child in node.filter((javalang.tree.MethodDeclaration, javalang.tree.ClassDeclaration)):
        line_number = child.position.line
        code_snippet = javalang.tree.Node.to_str(child)
        context = generator._get_context(child)
        comment = generator._generate_comment_for_snippet(code_snippet, type(child).__name__, context)
        comments[line_number] = comment
    return comments

def format_java_comment(comment: str, indent: int, style: str) -> List[str]:
    if style == "javadoc":
        return ([f'{" " * indent}/**'] + 
                [f"{' ' * indent} * {line}" for line in comment.split('\n')] + 
                [f'{" " * indent} */'])
    else:  # default to single-line comments
        return [f"{' ' * indent}// {line}" for line in comment.split('\n')]

LANGUAGE_PLUGIN = LanguagePlugin(
    name="java",
    file_extensions=[".java"],
    parse_function=parse_java,
    analyze_function=analyze_java,
    generate_comment_function=generate_java_comments,
    format_comment_function=format_java_comment
)
