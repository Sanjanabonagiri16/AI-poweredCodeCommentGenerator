import astroid
from typing import List, Dict, Any

# If LanguagePlugin is defined elsewhere, import it like this:
# from some_module import LanguagePlugin

# If LanguagePlugin is not defined elsewhere, let's define it here:
from dataclasses import dataclass

@dataclass
class LanguagePlugin:
    name: str
    file_extensions: List[str]
    parse_function: callable
    analyze_function: callable
    generate_comment_function: callable
    format_comment_function: callable

def parse_python(code: str) -> astroid.Module:
    return astroid.parse(code)

def analyze_python(node: astroid.NodeNG) -> Dict[str, Any]:
    context = {
        'imports': [],
        'functions': [],
        'classes': [],
    }
    for child in node.body:
        if isinstance(child, astroid.Import):
            context['imports'].extend(name for name, _ in child.names)
        elif isinstance(child, astroid.ImportFrom):
            context['imports'].extend(f"{child.modname}.{name}" for name, _ in child.names)
        elif isinstance(child, astroid.FunctionDef):
            context['functions'].append(child.name)
        elif isinstance(child, astroid.ClassDef):
            context['classes'].append(child.name)
    return context

def generate_python_comments(generator, node: astroid.Module, code: str) -> Dict[int, str]:
    comments = {}
    for child in node.body:
        if isinstance(child, (astroid.FunctionDef, astroid.ClassDef)):
            line_number = child.lineno
            code_snippet = astroid.unparse(child)
            context = generator._get_context(child)
            comment = generator._generate_comment_for_snippet(code_snippet, type(child).__name__, context)
            comments[line_number] = comment
    return comments

def format_python_comment(comment: str, indent: int, style: str) -> List[str]:
    if style == "google":
        return [f'{" " * indent}"""'] + [f"{' ' * (indent + 4)}{line}" for line in comment.split('\n')] + [f'{" " * indent}"""']
    elif style == "numpy":
        return [f'{" " * indent}"""'] + [f"{' ' * indent}{line}" for line in comment.split('\n')] + [f'{" " * indent}"""']
    else:  # default to single-line comments
        return [f"{' ' * indent}# {line}" for line in comment.split('\n')]

LANGUAGE_PLUGIN = LanguagePlugin(
    name="python",
    file_extensions=[".py"],
    parse_function=parse_python,
    analyze_function=analyze_python,
    generate_comment_function=generate_python_comments,
    format_comment_function=format_python_comment
)
