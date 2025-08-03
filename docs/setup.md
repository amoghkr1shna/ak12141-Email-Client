# KYMail Setup Guide

## Prerequisites
- Python 3.10 or higher
- UV package manager

## Installation

### 1. Install UV

If you don't already have UV installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Install Dependencies

```bash
git clone https://github.com/amoghkr1shna/ak12141-Email-Client.git
cd ak12141-Email-Client
uv sync --all-extras
```

## Development Setup

### Running Tests

Run all tests:
```bash
uv run pytest
```

Run specific test suites:
```bash
# Integration tests
uv run pytest tests/integration/

# End-to-end tests  
uv run pytest tests/e2e/

# Module-specific tests
uv run pytest src/message/tests/
```

Run with coverage:
```bash
uv run pytest --cov=src --cov-report=html
```

### Code Quality

Format code:
```bash
uv run ruff format .
```

Lint code:
```bash
uv run ruff check .
```

Type checking:
```bash
uv run mypy src/
```

### Building Documentation

```bash
uv run mkdocs build
uv run mkdocs serve  # For development
```

## CI/CD

The project uses CircleCI for continuous integration with the following pipeline:

1. **Setup**: Install UV and dependencies
2. **Code Quality**: Ruff formatting and linting checks
3. **Type Checking**: MyPy static analysis
4. **Testing**: Pytest with coverage reporting
5. **Documentation**: MkDocs build verification
6. **Artifacts**: Coverage reports and documentation

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Run the test suite: `uv run pytest`
6. Check code quality: `uv run ruff check .`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Development Guidelines

- Follow the existing protocol-based architecture
- Add comprehensive tests for new features
- Update documentation for any API changes
- Ensure all CI checks pass
- Use type hints throughout

## License

This project is licensed under the MIT License - see the LICENSE file for details.