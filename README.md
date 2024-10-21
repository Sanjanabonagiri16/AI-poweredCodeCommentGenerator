# 🤖 AI-Powered Code Comment Generator

An intelligent tool that automatically generates meaningful comments for your code across multiple programming languages.

## ✨ Features

- 🌐 Supports multiple programming languages (Python, JavaScript, Java, C++)
- 🧠 Uses advanced AI models for comment generation
- 🔄 Git integration for version control
- 🌈 Customizable comment styles (Google, NumPy, single-line)
- 📊 Code quality evaluation
- 📚 Learning resources generation
- 🖥️ Web interface for easy use
- 🔌 Extensible plugin system for adding new languages

## 🛠️ Installation

1. Clone the repository:   ```
   git clone https://github.com/yourusername/ai-code-comment-generator.git
   cd ai-code-comment-generator   ```

2. Install the required dependencies:   ```
   pip install nltk transformers torch spacy flask gitpython astroid esprima javalang pycparser scikit-learn   ```

3. Download the spaCy English model:   ```
   python -m spacy download en_core_web_sm   ```

4. Set up your local AI models:
   - Place your Qwen 2.5 or LLaMA model files in the `models/qwen2.5/` or `models/llama/` directory respectively.

## 🚀 Usage

### Command Line Interface

Generate comments for a single file:
