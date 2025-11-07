# questfoundry-cli

Command-line interface for QuestFoundry (Layer 7).

## Installation

```bash
pip install questfoundry-cli
```

Or install both library and CLI:

```bash
pip install questfoundry-py questfoundry-cli
```

## Quick Start

```bash
# Show help
qf --help

# List available schemas
qf schema list

# Show schema details
qf schema show hook_card

# Validate an artifact
qf validate artifact my-artifact.json --schema hook_card

# Show version
qf version
```

## Architecture

This tool (Layer 7) provides a user-friendly CLI for the QuestFoundry Python library (Layer 6).

```
Layer 6: Python Library (questfoundry-py)
    ↓
Layer 7: CLI (questfoundry-cli) ← You are here
```

## Commands

### Schema Management

```bash
# List all available schemas
qf schema list

# Show a specific schema
qf schema show hook_card

# Validate a schema file
qf schema validate hook_card
```

### Validation

```bash
# Validate an artifact against a schema
qf validate artifact my-file.json --schema hook_card

# Validate a Layer 4 envelope
qf validate envelope my-envelope.json
```

### Artifact Operations

```bash
# Create a new artifact interactively
qf artifact create --type hook_card --output my-artifact.json

# Get artifact info
qf artifact info my-artifact.json
```

## Development

### Setup

```bash
git clone https://github.com/pvliesdonk/questfoundry-cli
cd questfoundry-cli
git submodule add https://github.com/pvliesdonk/questfoundry-spec spec
uv sync
```

### Run locally

```bash
uv run qf --help
```

### Run tests

```bash
uv run pytest
```

### Run linter

```bash
uv run ruff check .
uv run mypy src
```

## Documentation

- [Specification](https://github.com/pvliesdonk/questfoundry-spec)
- [Layer 7 Implementation Plan](https://github.com/pvliesdonk/questfoundry-spec/tree/main/07-ui)
- [Python Library (questfoundry-py)](https://github.com/pvliesdonk/questfoundry-py)

## License

MIT

## Related Repositories

- [questfoundry-spec](https://github.com/pvliesdonk/questfoundry-spec) - Specification and schemas
- [questfoundry-py](https://github.com/pvliesdonk/questfoundry-py) - Python library
