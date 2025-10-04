# Contributing to pyasm6502

Thank you for your interest in contributing to pyasm6502! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project follows a code of conduct that ensures a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- Basic understanding of 6502 assembly language
- Familiarity with ACME assembler syntax (helpful but not required)

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pyasm6502.git
   cd pyasm6502
   ```

3. **Install development dependencies** (optional but recommended):
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the test suite** to ensure everything works:
   ```bash
   cd tests
   python run_tests.py
   ```

## Contributing Guidelines

### Areas Where Contributions Are Welcome

- **Bug fixes**: Fix issues reported in the bug tracker
- **Documentation**: Improve README, code comments, and documentation
- **Tests**: Add test cases for new features or edge cases
- **Performance**: Optimize assembly speed or memory usage
- **Features**: New ACME-compatible directives or functionality
- **Examples**: Assembly code examples and tutorials

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and reasonably sized
- Add comments for complex logic

### Commit Messages

Use clear, descriptive commit messages:

```
Good: "Fix symbol resolution for forward references in macros"
Bad: "fix bug"
```

Format: `type: description`

Common types:
- `fix`: Bug fixes
- `feat`: New features
- `docs`: Documentation changes
- `test`: Test additions or changes
- `refactor`: Code refactoring
- `perf`: Performance improvements

## Testing

### Running Tests

The project includes comprehensive test suites:

```bash
# Run all tests
cd tests
python run_tests.py

# Run quick functionality tests
python quick_test.py

# Run ACME compatibility tests
python check_acme_compatibility.py
```

### Writing Tests

When adding new features:

1. **Add test cases** to verify functionality
2. **Test edge cases** and error conditions
3. **Ensure backward compatibility** with existing ACME syntax
4. **Update compatibility tests** if adding new directives

### Test Structure

- `quick_test.py`: Basic functionality and regression tests
- `check_acme_compatibility.py`: ACME compatibility verification
- `run_tests.py`: Main test runner and orchestration

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
   ```bash
   cd tests
   python run_tests.py
   ```

2. **Check code style** (if using development dependencies):
   ```bash
   black .
   flake8 .
   mypy .
   ```

3. **Update documentation** if needed

4. **Add test cases** for new functionality

### Submitting a Pull Request

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear commits

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Test results showing all tests pass

### Pull Request Review

- Maintainers will review your PR
- Address any feedback or requested changes
- Ensure all CI checks pass
- Be patient - reviews may take time

## Reporting Bugs

### Before Reporting

1. **Check existing issues** to avoid duplicates
2. **Test with the latest version**
3. **Try to reproduce** the issue consistently

### Bug Report Template

When reporting bugs, please include:

```markdown
**Bug Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Assembly code that causes the issue
2. Command used to run the assembler
3. Expected vs actual output

**Environment**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- pyasm6502 version: [if known]

**Additional Context**
Any other relevant information, error messages, or screenshots.
```

### Example Assembly Code

Please provide minimal assembly code that reproduces the issue:

```assembly
; Minimal example demonstrating the bug
!cpu 6502

* = $C000

start:
    lda #$00
    ; Add the problematic code here
    rts
```

## Feature Requests

### Before Requesting

1. **Check existing issues** for similar requests
2. **Verify ACME compatibility** - features should align with ACME syntax
3. **Consider implementation complexity** and maintainability

### Feature Request Template

```markdown
**Feature Description**
A clear description of the requested feature.

**Use Case**
Explain why this feature would be useful and provide examples.

**ACME Compatibility**
Does this feature exist in ACME? If so, how should it behave?

**Implementation Considerations**
Any thoughts on how this might be implemented (optional).

**Additional Context**
Any other relevant information.
```

## Development Tips

### Understanding the Codebase

- `asm6502.py`: Command-line interface and entry point
- `assembler.py`: Core Assembler6502 class
- `package/`: Core assembler modules
  - `tokenizer.py`: Lexical analysis
  - `evaluator.py`: Expression evaluation
  - `directives.py`: ACME directive processing
  - `datastructures.py`: Core data structures

### Debugging

- Use `--verbose` flag for detailed output
- Check the debug system in `package/debug.py`
- Add temporary print statements for complex issues

### ACME Reference

When implementing ACME-compatible features, refer to:
- ACME documentation and source code
- Test cases in the compatibility test suite
- Existing directive implementations

## Questions?

If you have questions about contributing:

1. **Check the documentation** in the `docs/` folder
2. **Open a discussion** on GitHub
3. **Review existing issues** for similar questions

## Recognition

Contributors will be recognized in:
- GitHub contributor list
- Release notes for significant contributions
- Project documentation (for major contributions)

Thank you for contributing to pyasm6502!
