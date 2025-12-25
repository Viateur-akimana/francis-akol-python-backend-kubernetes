# Contributing to MLH Platform

Thank you for your interest in contributing to the Modular Learning Hub!

## Development Setup

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone git@github.com:YOUR_USERNAME/francis-akol-python-backend-assessment.git
   ```
3. **Set up development environment**
   - See [docs/deployment/local-setup.md](docs/deployment/local-setup.md)

## Branch Strategy

- `main` - Production-ready code
- `development` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

## Making Changes

1. **Create a feature branch**
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   black services/
   isort services/ --profile=black
   flake8 services/
   pytest tests/ -v
   ```

4. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in X"
   git commit -m "docs: update README"
   git commit -m "test: add tests for X"
   git commit -m "style: format code"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create PR to `development` branch
   - Fill out PR template
   - Request review

## Code Style

- **Python**: Follow PEP 8, use Black formatter
- **Imports**: Use isort with Black profile
- **Type hints**: Add type annotations
- **Docstrings**: Document public functions/classes
- **Tests**: Aim for 80%+ coverage

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code formatting |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance tasks |

## Pull Request Guidelines

- Clear, descriptive title
- Reference related issues
- Include tests for new code
- Update documentation
- Keep PRs focused and small

## Code Review

All PRs require at least one approval before merging.

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation
- Breaking changes

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce
- Provide environment details
- Add relevant logs/screenshots

## Questions?

Open a discussion or reach out to maintainers.

Thank you for contributing! 🎉
