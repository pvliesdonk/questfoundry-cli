# questfoundry-cli

A powerful command-line interface for QuestFoundry, the framework for AI-assisted creative writing. Build rich, engaging stories with intelligent assistance throughout the creative process.

**Layer 7** - The user-friendly CLI for the QuestFoundry ecosystem

## Features

- **Loop Execution**: Run QuestFoundry loops to guide your creative process (Story Spark, Hook Harvest, Lore Deepening, etc.)
- **Project Management**: Initialize and manage QuestFoundry projects
- **Schema & Validation**: Manage artifact schemas and validate data integrity
- **Provider Configuration**: Configure AI providers (OpenAI, Anthropic, local models, etc.)
- **Quality Checks**: Run comprehensive quality checks on your project artifacts
- **Configuration**: Manage project settings through a clean YAML-based config

## Installation

### From PyPI

```bash
pip install questfoundry-cli questfoundry-py
```

### For Development

```bash
git clone https://github.com/pvliesdonk/questfoundry-cli
cd questfoundry-cli
git submodule update --init
uv sync
uv run qf --help
```

## Quick Start

### 1. Initialize a Project

```bash
# Create a new QuestFoundry project
qf init my-project

# Navigate to the project
cd my-project

# Verify the project setup
qf status
```

### 2. Configure Your Providers

QuestFoundry can automatically detect providers from environment variables:

```bash
# Check available providers
qf provider list

# Configure OpenAI
export OPENAI_API_KEY=sk-...

# Or set it in the project config
qf config set providers.text.openai.api_key sk-...

# View all configuration
qf config
```

Supported providers:
- **Text Models**: OpenAI, Anthropic, Google Gemini, Cohere, Ollama (local)
- **Image Models**: Stability AI, DALL-E, Midjourney, A1111 (local)

### 3. Execute Your First Loop

QuestFoundry uses "loops" - guided workflows that leverage AI at different stages of your creative process:

```bash
# See all available loops
qf loops

# For Story Spark, first set a seed (in project config)
qf config set story_seed "A detective discovers a hidden civilization"

# Start with Story Spark (initial concept generation)
qf run story-spark

# Continue with Hook Harvest to develop story hooks
qf run hook-harvest

# Deepen your world lore
qf run lore-deepening
```

**Note**: Story Spark requires a seed. You can set it in the project config or via the `QUESTFOUNDRY_SEED` environment variable. Loop execution requires `questfoundry-py` to be installed.

**Available Loops:**

**Discovery** (Building Your Story):
- `story-spark` - Generate initial story concepts and hooks
- `hook-harvest` - Generate and collect compelling story hooks
- `lore-deepening` - Expand and deepen world lore

**Refinement** (Polishing Your Work):
- `codex-expansion` - Expand codex entries with rich detail
- `style-tuneup` - Polish and align content style

**Asset** (Multi-Media Support):
- `art-touchup` - Generate and refine artwork
- `audio-pass` - Generate audio assets
- `translation-pass` - Translate content to other languages

**Export** (Final Steps):
- `binding-run` - Generate player-facing views
- `narration-dry-run` - Test narration flow
- `gatecheck` - Run quality checks
- `post-mortem` - Analyze project outcomes
- `archive-snapshot` - Create archival snapshots

### 4. Manage Your Content

```bash
# List all artifacts in your project
qf list

# Show details about an artifact
qf show my-artifact

# Validate artifact against schemas
qf validate artifact my-file.json

# Run quality checks
qf check

# View detailed check results
qf check --verbose
```

### 5. Enable Logging for Debugging

Control logging levels to understand system behavior:

```bash
# Set log level for any command (error, warning, info, debug, trace)
qf --log-level debug run story-spark
qf --log-level info check

# Common log levels:
#   error   - Only show errors
#   warning - Show warnings and errors
#   info    - Show informational messages (default)
#   debug   - Show detailed debug information
#   trace   - Maximum verbosity (same as debug in Python)
```

## Configuration

QuestFoundry projects use YAML-based configuration:

```bash
# View current configuration
qf config

# Set a configuration value
qf config set providers.text.openai.api_key sk-...
qf config set providers.default.text openai

# Get a specific configuration value
qf config get providers.text.openai
```

## Architecture

```
Layer 2: Dictionary & Specification (Schemas, Loop definitions)
    ↓
Layer 4: Envelope (Data format for artifacts)
    ↓
Layer 6: Python Library (questfoundry-py) - Core logic & Showrunner
    ↓
Layer 7: CLI (questfoundry-cli) ← You are here
```

QuestFoundry provides a complete framework for AI-assisted creative writing, with each layer providing specific functionality.

## Command Reference

### Project Commands

```bash
# Initialize a new project
qf init [project-name]

# Show project status and workspace information
qf status

# List all artifacts in the project
qf list

# Show details about a specific artifact
qf show <artifact-id>
```

### Loop Execution (Core Workflow)

```bash
# List all available loops with descriptions
qf loops

# Execute a loop
qf run <loop-name> [--interactive]

# Example loops (configure seed in config for story-spark)
qf config set story_seed "A hidden kingdom beneath the sea"
qf run story-spark
qf run hook-harvest
qf run lore-deepening
qf run codex-expansion
qf run style-tuneup
```

**Requirements**: questfoundry-py is required for loop execution:
```bash
pip install questfoundry-py[openai]
# Or with all providers
pip install questfoundry-py[all-providers]
```

Loop execution uses the questfoundry-py Showrunner to intelligently guide your creative process, updating project artifacts and managing state automatically.

### Schema Management

```bash
# List all available schemas with titles
qf schema list

# Show a specific schema definition
qf schema show <schema-name>

# Validate a schema file
qf schema validate <schema-name>
```

### Validation

```bash
# Validate an artifact against its schema
qf validate artifact <file.json>

# Validate a Layer 4 envelope
qf validate envelope <envelope.json>

# Run quality checks on the entire project
qf check [--bars integrity,schema,required,naming] [--verbose]
```

### Configuration

```bash
# View all configuration
qf config

# Get a specific configuration value
qf config get providers.text.openai

# Set a configuration value
qf config set providers.text.openai.api_key sk-...

# List available configuration
qf config list
```

### Provider Management

```bash
# List all available providers and their configuration status
qf provider list

# Providers auto-detect from environment variables
export OPENAI_API_KEY=sk-...  # Auto-detected as 'auto-configured'
```

### Other Commands

```bash
# Show project history
qf history

# Search artifacts by keyword or criteria
qf search <query>

# Show version information
qf version

# Display QuestFoundry information
qf info
```

## Troubleshooting

### No project found

**Error**: `No project found in current directory`

**Solution**: Initialize a project first:
```bash
qf init my-project
cd my-project
```

### Provider not configured

**Error**: `Provider not configured`

**Solution**: Set up the provider using environment variables or config:
```bash
# Using environment variable (auto-detected)
export OPENAI_API_KEY=sk-...

# Or explicitly set in config
qf config set providers.text.openai.api_key sk-...
```

### Schema file not found

**Error**: `Schema not found: hook_card`

**Solution**: Make sure the spec submodule is initialized:
```bash
git submodule update --init
```

### UnicodeDecodeError on Windows

If you encounter encoding errors on Windows, ensure UTF-8 is properly configured:
```bash
# Set Python to use UTF-8
chcp 65001
set PYTHONIOENCODING=utf-8
```

### Enabling debug logging

Enable debug logging to see detailed logs from questfoundry-cli and questfoundry-py:
```bash
qf --log-level debug run story-spark
qf --log-level debug check
qf --log-level trace run hook-harvest
```

### Debugging loop execution

To debug loop execution and see what's happening:
```bash
qf --log-level debug run story-spark
```

## Development

### Setup

```bash
git clone https://github.com/pvliesdonk/questfoundry-cli
cd questfoundry-cli
git submodule update --init
uv sync
```

### Run locally

```bash
uv run qf --help
uv run qf init test-project
cd test-project
uv run qf status
```

### Run tests

```bash
uv run pytest                    # Run all tests
uv run pytest tests/commands/    # Run command tests only
uv run pytest -v                 # Verbose output
```

### Type checking and linting

```bash
uv run mypy src                  # Type checking
uv run ruff check .              # Linting
uv run ruff format src           # Auto-format code
```

### Pre-commit hooks

```bash
uv run pre-commit install        # Install hooks
uv run pre-commit run --all-files  # Run all hooks
```

## Contributing

Contributions are welcome! Please ensure:

1. Code passes `ruff check` and `mypy` type checking
2. Tests pass with `pytest`
3. Commit messages are clear and descriptive
4. Changes follow the existing code style

## Documentation

- [QuestFoundry Specification](https://github.com/pvliesdonk/questfoundry-spec)
- [Layer 7 UI Implementation](https://github.com/pvliesdonk/questfoundry-spec/tree/main/07-ui)
- [Python Library (questfoundry-py)](https://github.com/pvliesdonk/questfoundry-py)
- [Loop Definitions](./src/qf/data/loops.yml)

## License

MIT - See LICENSE file for details

## Support

For issues, questions, or suggestions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review existing [issues](https://github.com/pvliesdonk/questfoundry-cli/issues)
3. Create a new issue with details about your problem
4. Enable `--verbose` to provide logs when reporting issues

## Related Repositories

- [questfoundry-spec](https://github.com/pvliesdonk/questfoundry-spec) - Layer 2 specification and schemas
- [questfoundry-py](https://github.com/pvliesdonk/questfoundry-py) - Layer 6 Python library
- [questfoundry-spec (Layer 7 UI)](https://github.com/pvliesdonk/questfoundry-spec/tree/main/07-ui) - UI implementation details
