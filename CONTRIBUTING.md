# Contributing to Pedal Power

Thank you for your interest in contributing to Pedal Power! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use case and benefits
- Any implementation ideas you have

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes**
5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

## Development Setup

### Firmware Development

See [firmware/README.md](firmware/README.md) for firmware development setup.

Requirements:
- Pico SDK
- CMake 3.13+
- ARM GCC toolchain

### Server Development

#### Using Docker (Recommended)

```bash
cd server
docker-compose up -d
```

#### Local Development with UV

```bash
cd server/django_pedalpower
uv pip install -e ".[dev]"
```

## Code Style

### Python

- Follow PEP 8
- Use Black for formatting: `black .`
- Use Ruff for linting: `ruff check .`
- Maximum line length: 100 characters
- Type hints encouraged

### C (Firmware)

- Follow Pico SDK style guidelines
- Use meaningful variable names
- Comment complex logic
- Keep functions focused and small

## Testing

### Server Testing

Run tests with pytest:
```bash
cd server/django_pedalpower
uv run pytest
```

### Manual Testing

Use the test MQTT publisher:
```bash
cd server
python test_mqtt_publisher.py --broker localhost --rate 10
```

## Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Update documentation as needed
- Add tests for new features
- Ensure all tests pass
- Follow the existing code style
- Write clear commit messages
- Reference any related issues

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited in the release notes

## Documentation

When adding features, please update:
- Relevant README files
- Code comments
- API documentation (for server changes)
- INSTALL.md (if installation steps change)

## Questions?

Feel free to open an issue for questions or discussion!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
