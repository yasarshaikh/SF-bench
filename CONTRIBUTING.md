# Contributing to SF-Bench

Thank you for your interest in contributing to SF-Bench! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yasarshaikh/SF-bench/issues)
2. If not, create a new issue using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue using the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Explain:
   - The problem the feature would solve
   - Proposed solution
   - Benefits to the community

### Contributing Tasks

Tasks are the core of SF-Bench! We welcome contributions of real-world Salesforce development tasks.

#### Task Requirements

1. **Real-world scenario**: Based on actual Salesforce development challenges
2. **Clear problem description**: Well-defined problem statement
3. **Validation criteria**: Clear success criteria
4. **Reproducible**: Can be executed in a scratch org
5. **Documented**: Includes context and expected solution

#### Task Submission Process

1. Create a task JSON following the [task schema](docs/task-schema.md)
2. Test the task locally
3. Submit a pull request with:
   - Task JSON file
   - Brief description
   - Difficulty level
   - Category/tags

#### Task Categories

- **Bug Fix**: Fixing errors or issues
- **Feature**: Implementing new functionality
- **Refactor**: Improving code quality
- **Security**: Security-related tasks
- **Integration**: API or external system integration
- **Architecture**: System design and planning

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Write tests** for new functionality
5. **Ensure tests pass**: `pytest`
6. **Update documentation** if needed
7. **Commit your changes**: Use clear, descriptive commit messages
8. **Push to your fork**: `git push origin feature/your-feature-name`
9. **Create a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and small
- Add comments for complex logic

### Testing

- Write tests for new features
- Ensure all existing tests pass
- Aim for >80% code coverage
- Test edge cases and error conditions

### Documentation

- Update README.md if adding features
- Add docstrings to new functions/classes
- Update relevant documentation files
- Include examples for new features

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yasarshaikh/SF-bench.git
   cd SF-bench
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Pull Request Process

1. **Update CHANGELOG.md** with your changes
2. **Ensure all tests pass**
3. **Update documentation** if needed
4. **Request review** from maintainers
5. **Address feedback** promptly
6. **Wait for approval** before merging

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Contact maintainers directly

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Recognized in release notes
- Featured in project documentation

Thank you for contributing to SF-Bench! 🎉

