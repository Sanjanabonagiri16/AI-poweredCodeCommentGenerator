import ast
import nltk
import argparse
import logging
import json
import hashlib
import os
from typing import List, Dict, Any, Optional, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import spacy
import git
from flask import Flask, render_template, request, jsonify
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Language-specific parsers
import astroid  # for Python
import esprima  # for JavaScript
import javalang  # for Java
import pycparser  # for C++

# Git integration
from git_manager import GitManager

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class CodeCommentGenerator:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize local model
        model_name = config.model_name  # e.g., "qwen2.5" or "llama"
        self.tokenizer = AutoTokenizer.from_pretrained(f"./models/{model_name}")
        self.model = AutoModelForCausalLM.from_pretrained(f"./models/{model_name}")
        
        # Initialize other components
        self.tfidf_vectorizer = TfidfVectorizer()
        self.git_manager = GitManager(os.getcwd())
        self.cache = self._load_cache()

    def _load_cache(self):
        try:
            with open(self.config.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache(self):
        with open(self.config.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def analyze_code(self, code: str) -> Any:
        if self.config.language == 'python':
            return astroid.parse(code)
        elif self.config.language == 'javascript':
            return esprima.parseScript(code)
        elif self.config.language == 'java':
            return javalang.parse.parse(code)
        elif self.config.language == 'cpp':
            return pycparser.c_parser.CParser().parse(code)
        else:
            raise ValueError(f"Unsupported language: {self.config.language}")

    def generate_comment(self, code_snippet: str, context: Dict[str, Any]) -> str:
        prompt = self._create_prompt(code_snippet, context)
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=150, num_return_sequences=1)
        
        comment = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return comment

    def _create_prompt(self, code_snippet: str, context: Dict[str, Any]) -> str:
        return f"Generate a detailed comment for this {self.config.language} code:\n\nCode: {code_snippet}\nContext: {json.dumps(context)}\n\nComment:"

    def process_file(self, file_path: str) -> None:
        try:
            with open(file_path, 'r') as file:
                code = file.read()

            tree = self.analyze_code(code)
            comments = self._generate_comments_for_tree(tree, code)
            updated_code = self._insert_comments(code, comments)

            if self.config.write_to_file:
                with open(file_path, 'w') as file:
                    file.write(updated_code)
                self.logger.info(f"Updated file: {file_path}")
                
                # Update Git history
                self.git_manager.commit_changes(file_path, "Updated comments")
            else:
                print(updated_code)

            self._save_cache()

        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")

    def _generate_comments_for_tree(self, tree: Any, code: str) -> Dict[int, str]:
        comments = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                line_number = node.lineno
                code_snippet = ast.get_source_segment(code, node)
                context = self._get_context(node)
                comment = self.generate_comment(code_snippet, context)
                comments[line_number] = comment
        return comments

    def _get_context(self, node: ast.AST) -> Dict[str, Any]:
        context = {
            'type': type(node).__name__,
            'name': getattr(node, 'name', ''),
            'docstring': ast.get_docstring(node),
            'complexity': self._analyze_complexity(node),
        }
        return context

    def _analyze_complexity(self, node: ast.AST) -> str:
        # Implement complexity analysis (e.g., cyclomatic complexity)
        # This is a placeholder implementation
        return "moderate"

    def _insert_comments(self, code: str, comments: Dict[int, str]) -> str:
        lines = code.split('\n')
        for line_number, comment in sorted(comments.items(), reverse=True):
            indent = len(lines[line_number - 1]) - len(lines[line_number - 1].lstrip())
            comment_lines = [f"{' ' * indent}# {line}" for line in comment.split('\n')]
            lines[line_number - 1:line_number - 1] = comment_lines
        return '\n'.join(lines)

    def evaluate_code_quality(self, code: str) -> Dict[str, Any]:
        # Implement code quality evaluation
        # This is a placeholder implementation
        return {
            'complexity': 'moderate',
            'maintainability': 'good',
            'documentation_quality': 'needs improvement'
        }

    def generate_learning_resources(self, code: str) -> Dict[str, Any]:
        # Generate learning resources based on the code
        # This is a placeholder implementation
        return {
            'best_practices': ['Use meaningful variable names', 'Write modular code'],
            'further_reading': ['https://docs.python.org/3/tutorial/']
        }

# Flask app setup
app = Flask(__name__)
generator = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_comments', methods=['POST'])
def generate_comments():
    code = request.json['code']
    language = request.json['language']
    comment_style = request.json['comment_style']

    config = argparse.Namespace(
        write_to_file=False,
        comment_style=comment_style,
        cache_file="comment_cache.json",
        language=language
    )

    global generator
    if generator is None or generator.config != config:
        generator = CodeCommentGenerator(config)

    tree = generator.analyze_code(code)
    comments = generator._generate_comments_for_tree(tree, code)
    updated_code = generator._insert_comments(code, comments)
    
    return jsonify({
        'commented_code': updated_code,
        'quality_report': generator.evaluate_code_quality(code),
        'learning_resources': generator.generate_learning_resources(code)
    })

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Code Comment Generator")
    parser.add_argument("path", help="Path to the file or directory to process")
    parser.add_argument("--write", action="store_true", help="Write changes to the file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--comment-style", choices=["google", "numpy", "single-line"], default="google", help="Comment style to use")
    parser.add_argument("--cache-file", default="comment_cache.json", help="Path to the cache file")
    parser.add_argument("--language", default="python", choices=["python", "javascript", "java", "cpp"], help="Programming language of the input files")
    parser.add_argument("--web", action="store_true", help="Start the web interface")
    parser.add_argument("--model", default="qwen2.5", choices=["qwen2.5", "llama"], help="Local model to use for comment generation")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    config = argparse.Namespace(
        write_to_file=args.write,
        comment_style=args.comment_style,
        cache_file=args.cache_file,
        language=args.language,
        model_name=args.model
    )

    generator = CodeCommentGenerator(config)

    if args.web:
        app.run(debug=True)
    elif os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(f'.{args.language}'):
                    file_path = os.path.join(root, file)
                    generator.process_file(file_path)
    else:
        generator.process_file(args.path)

if __name__ == "__main__":
    main()
