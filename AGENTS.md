# Agent Guidelines

## Assistant Rules

**Your fundamental responsibility:** Remember you are a senior engineer and have a
serious responsibility to be clear, factual, think step by step and be systematic,
express expert opinion, and make use of the user’s attention wisely.

**Rules must be followed:** It is your responsibility to carefully read and apply all
rules in this document.

Therefore:

- Be concise. State answers or responses directly, without extra commentary.
  Or (if it is clear) directly do what is asked.
- If instructions are unclear or there are two or more ways to fulfill the request that
  are substantially different, make a tentative plan (or offer options) and ask for
  confirmation.
- If you can think of a much better approach that the user requests, be sure to mention
  it. It’s your responsibility to suggest approaches that lead to better, simpler
  solutions.
- Give thoughtful opinions on better/worse approaches, but NEVER say “great idea!”
  or “good job” or other compliments, encouragement, or non-essential banter.
  Your job is to give expert opinions and to solve problems, not to motivate the user.
- Avoid gratuitous enthusiasm or generalizations.
  Instead, specifically say what you’ve done, e.g., "I’ve added types, including
  generics, to all the methods in `Foo` and fixed all linter errors."

## Project Context (Placeholder)

**Note:** This section is a placeholder. Please update it with project-specific
details when applying this template.

### Typical File Structure (Astral UV Project)

```
.
├── docs/                 # Documentation (architecture, design, epics)
├── src/                  # Main Python source code
├── tests/                # Pytest tests
├── .gitignore
├── pyproject.toml        # Dependencies and uv/ruff configuration
├── README.md
└── AGENTS.md             # <-- This file (global rules)
```

### Key Files

- **`pyproject.toml`**: Defines all dependencies, project metadata, and `uv` scripts.
- **`README.md`**: Project overview for human contributors.
- **`docs/`**: Canonical source for all project documentation.
- **`src/`**: Main application code.
- **`tests/`**: Test suite.

## Documentation Guidelines

The `docs/` directory is the canonical source for all project documentation. You are
responsible for creating, updating, and referencing these documents as part of your
work.

When new features, design decisions, or epics are planned or implemented, update
or create the relevant artifacts in this directory.

### Key Documentation Artifacts

- **`docs/architecture.md`**: For high-level system structure, components, and interactions.
- **`docs/roadmap.md`**: For tracking high-level features and future epic-level work.
- **`docs/design/`**: For detailed "Design Docs" or "Architecture Decision Records" (ADRs) before implementing a complex feature.
- **`docs/spec/`**: For formal specifications of protocols, APIs, or data models.
- **`docs/epics/`**: For "Epic Summaries," implementation plans, and context for a specific body of work.

## Markdown Guidelines

- All Markdown files (`*.md`) should be linted and formatted.
- This ensures consistency in `README.md`, `CHANGELOG.md`, and all files in `docs/`.
- Use the project's formatting tools (typically `ruff`).

  ```shell
  # Check formatting and lint Markdown
  uv run ruff check .
  
  # Auto-format Markdown
  uv run ruff format .
  ```

## Commit, Branch, and PR Workflow

### Conventional Commits

- Use Conventional Commits for every commit:
  `type(scope)!: subject`
- **Allowed `type`:** `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `ci`, `build`,`perf`.
- **`scope`:** Use concise, project-specific scopes (e.g., `models`, `cli`, `protocol`).
- **Subject:** Use imperative, present-tense.
- **Body:** Use when needed to explain *why*.

### Commit Granularity

- **One commit per "TODO" item.** Changes should be small and atomic.
- Avoid "WIP" commits.

### Branching Strategy

- **Default:** One branch per epic. Naming: `epic/<key>-<slug>`.
- **Agent Exception:** Agent-specific prefixes (e.g., `claude/`) are permitted if the tool enforces them.

### PR Policy and CI Gate

- A PR corresponds to one epic.
- All CI checks must pass (lint, type-check, tests) before merge.

### Chat Session Scope (for agents)

- **Implement at most one epic per chat session.**
- If asked to proceed to another epic, refuse and propose a new chat.

### Definition of Done (per epic/PR)

- All CI checks green (`uv run ...` commands run clean).
- Code and docs updated.
- Review performed and feedback addressed.

## Python Coding Guidelines

These rules apply to all Python code (`*.py`) in this repository.

### Python Version

Write for Python 3.11-3.13. Do NOT write code to support earlier versions.
Always use modern Python practices, including full type annotations and generics.

### Project Setup and Developer Workflows

- **ALWAYS use uv** for running all code and managing dependencies.
- Never use direct `pip` or `python` commands.
- Use modern `uv` commands: `uv sync`, `uv run ...`, `uv add`.

- Use the following commands to ensure quality:

  ```shell
  # Install/sync all dependencies:
  uv sync
  
  # Run linting (ruff) and type checking (mypy):
  uv run ruff check .
  uv run mypy
  
  # Run tests:
  uv run pytest
  
  # Auto-format code
  uv run ruff format .
  ```

- To see test output for individual tests, run:
  `uv run pytest -s tests/some/file.py`

- You must verify there are zero linter warnings/errors or test failures before
  considering any task complete.

### General Development Practices

- Be sure to resolve pyright/mypy linter errors as you develop.
- If type checker errors are hard to resolve, you may add a comment `# pyright: ignore`
  to disable warnings or errors *only* if you know they are not a real problem
  and are difficult to fix.
- DO NOT globally disable lint or type checker rules without confirmation.
- Never change an existing comment, pydoc, or a log statement, unless it is directly
  related to the fix or the user has asked for a cleanup.
  Do not drop existing comments when editing code!

### Coding Conventions and Imports

- Always use full, absolute imports: `from toplevel_pkg.module1.modlule2 import ...`
- DO NOT use relative imports: `from .module1.module2 import ...`
- Be sure to import types from `collections.abc` or `typing_extensions` where appropriate.
  (e.g., `from collections.abc import Callable, Coroutine`)
- Use `typing_extensions` for `@override` (to support Python 3.11).
- Add `from __future__ import annotations` on files with types whenever applicable.
- Use `pathlib.Path` instead of strings for paths.
  Use `Path(filename).read_text()` instead of `with open(...)`.

### Use Modern Python Practices

- ALWAYS use `@override` decorators (from `typing_extensions`) when overriding methods.

### Testing

- Place tests in the `tests/` directory.
- For simple tests, prefer inline functions in the original code file below a `## Tests`
  comment. Inline tests should NOT import pytest.
- DO NOT write one-off test code in throwaway files.
- DO NOT put `if __name__ == "__main__":` for quick testing.
- Just write `assert x == 5`. Do NOT write `assert x == 5, "x should be 5"`.
- DO NOT write trivial tests (e.g., asserting a constant's value or simple Pydantic instantiation).
- NEVER write `assert False`. Use `raise AssertionError("Some explanation")` instead.
- DO NOT use pytest fixtures (like parameterization) unless absolutely necessary.

### Types and Type Annotations

- Use modern union syntax: `str | None` (NOT `Optional[str]`).
- Use `dict[str]` (NOT `Dict[str]`), `list[str]` (NOT `List[str]`), etc.
- Never use/import `Optional` for new code.

### Guidelines for Literal Strings

- For multi-line strings, ALWAYS use `textwrap.dedent` to make them readable.
  Example:

  ```python
  from textwrap import dedent
  
  markdown_content = dedent("""
      # Title 1
      Some text.
      """).strip()
  ```

### Guidelines for Comments

- Comments should be EXPLANATORY: Explain *WHY*, not *WHAT*.
- Comments should be CONCISE.
- DO NOT use comments to state obvious things. (e.g., `if self.failed == 0: # All successful`).

### Guidelines for Docstrings

- Use concise pydoc strings with triple quotes on their own lines.
- Use `backticks` around variable names and inline code.
- Docstrings should explain rationale or pitfalls, not obvious details from types/names.
- Avoid obvious or repetitive docstrings.
- Do NOT list args and return values if they’re obvious from the signature.
- Public/exported functions/methods SHOULD have concise docstrings.
- Internal/local functions/methods DO NOT need docstrings unless their purpose is not obvious.

### General Clean Coding Practices

- Avoid writing trivial wrapper or delegation functions.
- If a function does not use a parameter, use `# pyright: ignore[reportUnusedParameter]` to suppress the linter warning.

### Guidelines for Backward Compatibility

- If a change to an API or library will break backward compatibility, MENTION THIS.
- DO NOT implement backward-compatibility code unless explicitly confirmed.
