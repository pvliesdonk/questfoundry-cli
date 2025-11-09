# QuestFoundry CLI

Development guidelines for AI assistants (Claude Code)

## Quick Start

1. **Read these files first**:
   - `instructions.md` - Overall project structure and standards
   - `conventional-commits.md` - Commit message format
   - `epic-workflow.md` - Epic-based development process

2. **Verify environment**:
   ```bash
   uv sync                 # Install dependencies
   uv run pytest           # Run tests
   uv run mypy src/        # Type checking
   uv run ruff check .     # Linting
   ```

3. **Check current state**:
   - Review recent commits: `git log --oneline -10`
   - Check current branch: `git branch --show-current`
   - Review open work: Check `spec/07-ui/IMPLEMENTATION_PLAN.md`

## Key Rules

1. **Always use conventional commits**
2. **One feature = one commit (minimal commits strategy)**
3. **One epic = one branch (never reuse branches)**
4. **Write PR text for each epic** (`.claude/pr-description-epic-N.md`)
5. **Test before committing** (Tests + Mypy + Ruff all passing)
6. **Type hints required**
7. **At least one round of reviews** before marking epic done
8. **Review feedback must be addressed**
9. **Branch names must include session ID**

## Files Structure

```
.claude/
├── README.md                    # This file
├── instructions.md              # Main instructions
├── conventional-commits.md      # Commit standards
└── epic-workflow.md             # Development workflow
```

## Before Making Changes

1. Check implementation plan: `spec/07-ui/IMPLEMENTATION_PLAN.md`
2. Check implementation updates: `docs/LAYER_7_UPDATES_FOR_EPIC_7_8.md`
3. Review existing patterns in `src/qf/`
4. Run validation: `uv run pytest && uv run mypy src/ && uv run ruff check .`

## Need Help?

- Spec documentation: `spec/` directory
- Layer 3 schemas: `spec/03-schemas/`
- Layer 4 protocol: `spec/04-protocol/`
- Layer 5 prompts: `spec/05-prompts/`
- Layer 7 plan: `spec/07-ui/IMPLEMENTATION_PLAN.md`
- Implementation updates: `docs/LAYER_7_UPDATES_FOR_EPIC_7_8.md`

## Current Progress

**Completed Epics**:
- ✅ Epic 1: Project Foundation
- ✅ Epic 2: Core Commands
- ✅ Epic 3: Configuration & Providers
- ✅ Epic 4: Validation & Quality
- ✅ Epic 5: Loop Execution (merged into main)
- ✅ Epic 6: Asset Generation (merged into main)
- ✅ Epic 7: Quickstart Workflow (merged into main)
- ✅ Epic 5 Updates: Multi-iteration Loop Tracking (merged into main)

**In Progress**:
- 🔄 Epic 8: Export & Views (branch: to be created)

**Progress**: 8/12 epics complete (67%)

**Next**: Epic 8: Export & Views
