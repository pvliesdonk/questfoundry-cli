# Conventional Commits Quick Reference

## Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Common Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | New feature | Minor (0.x.0) |
| `fix` | Bug fix | Patch (0.0.x) |
| `docs` | Documentation | None |
| `style` | Formatting | None |
| `refactor` | Code restructuring | None |
| `perf` | Performance | Patch |
| `test` | Tests | None |
| `chore` | Maintenance | None |
| `ci` | CI/CD | None |

## Breaking Changes

Add `!` after type or `BREAKING CHANGE:` in footer:

```bash
feat(commands)!: change command structure

BREAKING CHANGE: qf validate now requires --schema flag
```

## Examples for This Project

```bash
# Adding new functionality
feat(commands): add qf init command
feat(commands): implement qf list command
feat(formatting): add artifact table formatter
feat(interactive): add quickstart guided mode

# Fixing bugs
fix(commands): handle missing project gracefully
fix(formatting): correct progress bar alignment
fix(validation): fix schema path resolution

# Refactoring
refactor(commands): simplify error handling
refactor(formatting): extract table creation logic

# Tests
test(commands): add tests for qf init
test(formatting): add table formatter tests

# Documentation
docs: update installation instructions
docs(commands): document qf run command

# Maintenance
chore(deps): update typer to v0.9.1
chore: update spec submodule

# CI/CD
ci: add package build workflow
ci: fix workflow checkout
```

## Rules

1. **Imperative mood**: "add" not "added" or "adds"
2. **Lowercase**: subject line should be lowercase
3. **No period**: don't end subject with a period
4. **Max 72 chars**: keep subject line concise
5. **Body optional**: use for complex changes
6. **Reference issues**: `Closes #123` in footer

## Multi-line Example

```bash
feat(commands): implement qf quickstart command

- Add guided mode with checkpoints
- Add interactive mode with agent questions
- Implement loop sequencing
- Add progress tracking

This enables users to create projects through a
guided workflow with checkpoints after each loop.

Refs: #15
```

## Quick Tips

- **One commit = one logical change**
- **Separate features = separate commits**
- **Tests in same commit** as the code they test
- **Breaking changes** must be clearly marked
- **Scope helps** with changelog generation

## Bad Examples (Don't Do This)

```bash
❌ "fixed stuff"
❌ "WIP"
❌ "asdf"
❌ "Updated files"
❌ "feat: Added feature"  # (use lowercase, no past tense)
❌ "feat(commands) Add command"  # (missing colon)
```

## Good Examples

```bash
✅ feat(commands): add qf init command
✅ fix(formatting): handle empty tables gracefully
✅ test(commands): add qf list tests
✅ docs: update README with quick start guide
✅ chore(deps): update dependencies
```
