# 🌎 World Builder

[![ci](https://github.com/SeedyROM/world-builder/workflows/CI/badge.svg)](https://github.com/SeedyROM/world-builder/actions)
[![coverage](https://codecov.io/gh/SeedyROM/world-builder/branch/main/graph/badge.svg)](https://codecov.io/gh/SeedyROM/world-builder)

## What is this?

World Builder is a tool to help you prompt AI models to generate a structured output for code changes that can be easily parsed and applied to a codebase.

**It's not complicated, but the code itself is meant to showcase a more modern way of writing Python code, using type hints, dataclasses, and other modern features, tooling.**

## Development
To get started with development, you can clone the repository and install the dependencies:

- `poetry install`
- `poetry run pre-commit install`

To run the tests, you can use:
- `poetry run test`

Or if you want to run the tests with coverage:
- `poetry run test-cov`

## Usage

This is not the real usage, but for how it's build you just run:

```bash
poetry run cli
```

This will run the CLI and show you the only currenly supported output, which is not giving any args.
It shows you the expected prompt for the LLM, copies it to your clipboard, and then expects you to paste the response back into the CLI.

## Contributing
If you want to contribute, feel free to open an issue or a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
This project is inspired by the need to have a structured way to prompt AI models to generate code changes that can be easily parsed and applied to a codebase. It is built with the intention of showcasing modern Python features and best practices.