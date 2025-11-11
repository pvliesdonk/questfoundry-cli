# Refactor vs Rewrite Analysis

## Current State Assessment

After deep dive analysis, the CLI has:
- **4,200 lines** of command implementation code
- **134 occurrences** of simulation/placeholder code
- **218 passing tests** (but testing simulation, not real functionality)
- **Good UX foundation** (Rich UI, progress tracking, formatting)
- **Bad architecture** (not a thin wrapper, duplicates library)

## Option 1: Refactor Existing Code

### Keep:
- ✅ Test infrastructure (pytest setup, fixtures)
- ✅ Rich-based formatting modules (`formatting/`)
- ✅ Shell completion system (`completions/`)
- ✅ Typer CLI structure (well-organized command groups)
- ✅ Project discovery utilities (`find_project_file`, etc.)
- ✅ Interactive prompts (`qf quickstart` flow)

### Rewrite:
- 🔄 `commands/run.py` - Replace 178 lines with ~20 line wrapper
- 🔄 `commands/quickstart.py` - Use real loop execution
- 🔄 `commands/init.py` - Use WorkspaceManager
- 🔄 `commands/export.py` - Use BookBinder role
- 🔄 `commands/bind.py` - Use BookBinder role
- 🔄 `commands/check.py` - Use Gatekeeper role
- 🔄 `commands/status.py` - Use WorkspaceManager queries
- 🔄 `commands/provider.py` - Use ProviderRegistry

### Delete:
- ❌ `data/loops.yml` - Use LoopRegistry instead
- ❌ All `time.sleep()` calls
- ❌ All "Layer 6 coming soon" messages
- ❌ Placeholder/simulation functions

### Estimated Effort:
- **3-5 days** of focused refactoring
- **Risk:** May discover more issues as you go
- **Benefit:** Keep tests, UX, project structure

---

## Option 2: Start From Scratch (Recommended)

### Approach:

#### Phase 1: Study questfoundry-py v0.5.0 (1 day)
1. Read actual source code of:
   - `questfoundry/loops/` - Understand loop system
   - `questfoundry/roles/` - Understand role system
   - `questfoundry/state/` - Understand workspace management
   - `questfoundry/providers/` - Understand provider system

2. Write exploration scripts:
   ```python
   # explore_loops.py
   from questfoundry.loops import LoopRegistry
   registry = LoopRegistry()
   for loop in registry.list_loops():
       print(f"{loop.loop_id}: {loop.description}")
       print(f"  Roles: {loop.primary_roles}")
       print(f"  Outputs: {loop.output_artifacts}")
   ```

3. Document what **actually exists** vs what you **need**

#### Phase 2: Write New Spec (1 day)
Create `SPEC_V2.md` based on reality:
```markdown
# CLI Spec V2 (Based on questfoundry-py v0.5.0)

## Core Commands (Thin Wrappers)

### qf init [path]
Wrapper around: WorkspaceManager.initialize()
Lines of code: ~30
Dependencies: questfoundry.state.WorkspaceManager

### qf run <loop-name>
Wrapper around: LoopRegistry.get_loop().execute()
Lines of code: ~40 (includes progress display)
Dependencies: questfoundry.loops.{LoopRegistry, LoopContext}

### qf status
Wrapper around: WorkspaceManager queries
Lines of code: ~50 (includes formatting)
Dependencies: questfoundry.state.WorkspaceManager
...
```

#### Phase 3: Implement Incrementally (3-5 days)
Build one command at a time with **real integration**:

```
Day 1: qf init (with WorkspaceManager)
Day 2: qf run (with LoopRegistry)
Day 3: qf generate (with RoleRegistry)
Day 4: qf status, qf list (with WorkspaceManager)
Day 5: qf export, qf bind (with BookBinder)
```

Each command:
1. Write against real library
2. Test with real library (mocked LLM providers)
3. Add basic tests
4. Move to next command

#### Phase 4: Port UX Polish (1-2 days)
Copy over the **good parts** from old CLI:
- Rich formatting utilities
- Progress tracking patterns
- Interactive prompts
- Shell completion

### Total Estimated Effort:
- **6-8 days** total
- **Higher confidence** of correctness
- **No technical debt** from the start
- **Incremental testing** with real library

---

## Comparison Matrix

| Aspect | Refactor | Rewrite |
|--------|----------|---------|
| Time | 3-5 days | 6-8 days |
| Risk | Medium (unknown issues) | Low (clean slate) |
| Learning | Minimal | Deep (study library) |
| Test Reuse | High (218 tests) | Low (must rewrite) |
| UX Reuse | High (keep all) | Medium (port good parts) |
| Technical Debt | Medium (residual issues) | None (clean) |
| Correctness Confidence | Medium | High |
| Maintainability | Medium | High |

---

## Specific Issues That Make Rewrite Attractive

### 1. The Loop System Mismatch
CLI defines 13 loops (3 missing from library), library has 11 loops (1 missing from CLI).
- **Refactor:** Must reconcile, possibly contribute to upstream
- **Rewrite:** Just use what library has, document gaps

### 2. The Simulation Architecture
Commands are built around **faking work**, not **doing work**.
- **Refactor:** Must untangle simulation from real code
- **Rewrite:** Build around real library calls from start

### 3. The Misunderstood Spec
Current code was built on spec that assumed things weren't ready.
- **Refactor:** Must reinterpret spec while refactoring
- **Rewrite:** Write new spec based on what actually exists

### 4. The Test Suite
Tests verify simulation behavior, not real behavior.
- **Refactor:** Must rewrite tests anyway to test real integration
- **Rewrite:** Write correct tests from start

---

## My Recommendation: Rewrite (But Keep Reference)

### Strategy:

1. **Keep old repo** as `questfoundry-cli-old` (for reference)
   - Good UX patterns to copy
   - Test structure ideas
   - Rich formatting examples

2. **Create new repo** as `questfoundry-cli` (clean slate)
   - Study questfoundry-py first (1 day)
   - Write spec based on reality (1 day)
   - Implement incrementally (5 days)
   - Port UX polish (1 day)

3. **Advantages:**
   - Learn library deeply before building
   - No technical debt
   - Clean git history
   - Can cherry-pick good code from old repo
   - Much easier to maintain long-term

4. **What to Port from Old:**
   - Rich formatting patterns (`formatting/` module patterns)
   - Progress tracking approach
   - Interactive prompt flows
   - Shell completion system structure
   - Test infrastructure setup (pytest.ini, fixtures)

---

## Decision Framework

### Choose Refactor If:
- [ ] Time pressure (need CLI in 3-5 days)
- [ ] Don't want to study library deeply
- [ ] Want to preserve exact test suite
- [ ] Comfortable with residual technical debt

### Choose Rewrite If:
- [x] Want to understand questfoundry-py deeply
- [x] Value long-term maintainability
- [x] Want confidence in correctness
- [x] Can invest 6-8 days total
- [x] Prefer clean architecture

---

## Next Steps (If Rewrite)

1. **Study Phase** (Day 1)
   ```bash
   cd /tmp
   git clone questfoundry-py
   cd questfoundry-py
   # Read source code of loops, roles, state, providers
   # Write exploration scripts
   # Document findings in LIBRARY_ANALYSIS.md
   ```

2. **Spec Phase** (Day 2)
   ```bash
   # Create new spec based on library reality
   # Write SPEC_V2.md with:
   # - Commands (what they wrap)
   # - Expected LOC for each command
   # - Integration points
   # - What NOT to implement (avoid duplication)
   ```

3. **Prototype Phase** (Day 3)
   ```bash
   # Create minimal working prototype
   # Just: qf init, qf run story-spark
   # Verify real integration works
   # ~200 lines total
   ```

4. **Build Phase** (Days 4-7)
   ```bash
   # Implement remaining commands
   # Add tests
   # Add UX polish
   ```

5. **Port Phase** (Day 8)
   ```bash
   # Copy formatting utilities from old CLI
   # Copy shell completion system
   # Polish UX
   ```

---

## Cost-Benefit Analysis

### Refactor Costs:
- 3-5 days engineering
- Risk of discovering more issues
- Technical debt remains
- Tests need rewriting anyway
- Spec still wrong

### Rewrite Costs:
- 6-8 days engineering
- Must study library deeply
- Must rewrite tests

### Rewrite Benefits:
- **Deep understanding** of questfoundry-py
- **Clean architecture** (true thin wrapper)
- **Correct spec** (based on reality)
- **Maintainable** codebase
- **Confidence** in correctness
- **Good foundation** for future work

### Net Benefit:
Spending extra 3 days upfront saves months of debugging and refactoring later.

---

## Conclusion

**Recommendation: Rewrite with library-first approach**

The current CLI was built on false assumptions about the library. Rather than untangling those assumptions while refactoring, it's better to:

1. Study the library deeply
2. Write a new spec based on reality
3. Build incrementally with real integration
4. Port the good UX elements from old CLI

The old CLI isn't a total loss - it has good patterns to reference. But the core architecture is fundamentally wrong, and fixing it is harder than building it right from scratch.

**Time investment:** 6-8 days
**Long-term payoff:** Years of maintainability
**Risk:** Low (you'll understand library deeply)
