# Refactoring God Files

This reference defines the strict, behavior-preserving decomposition protocol for refactoring giant, monolithic "God files" into cohesive, maintainable modules.

## 5-Step Behavior-Preserving Decomposition Protocol

### 1. Baseline & Characterization Gate
Never refactor blind! Before altering any code:
- **Measure:** Document the file/class/function LOC, cyclomatic complexity, and dependencies.
- **Map:** Trace responsibilities, internal state, and external callers.
- **Test:** Run the existing test suite. If test coverage is missing or inadequate, **write characterization tests at public seams FIRST**. Ensure the baseline is green.

### 2. Responsibility Clustering
Partition a `600-5,000+` LOC God file into cohesive responsibilities. A typical application should separate:
- **Domain Logic**: Core business rules and invariants.
- **Persistence/Repository**: Database access and queries.
- **External Adapters**: 3rd-party API clients and SDK wrappers.
- **Transport/DTO Mapping**: HTTP controllers, JSON parsing, validation.
- **Pure Helpers**: Stateless, side-effect-free utility functions.
*Note: Never create a new `utils2` or `misc` junk drawer. Name modules by their specific domain responsibility.*

### 3. Chunked Execution (`<=200` LOC per step)
Avoid "big bang" rewrites. Execute the refactor in small, verifiable chunks:
- **Extract:** Move one cohesive function group, Strategy handler, or collaborator class at a time (max `200` LOC).
- **Rewire:** Update imports and callers immediately.
- **Verify:** Run the test suite after *every single chunk*.
- **Rollback:** If tests go red, rollback the current chunk immediately, reassess, and try a smaller step.

### 4. DRY Consolidation Rules
Apply deduplication carefully, avoiding the "Wrong-DRY" trap:
- **`>80%` similarity in the SAME domain** or `>=30` LOC shared block ➔ **Extract** into a parameterized function or strategy.
- **`>50%` cross-module structural similarity** (in generic infrastructure) ➔ **Extract** into a shared abstraction.
- **`<50%` similarity OR distinct business domains** ➔ **Keep separate!** Do not couple independent lifecycles just to save a few lines of code.

### 5. Cleanup & LOC Delta Audit
Ensure the codebase is left in a pristine state:
- **One Implementation Per Feature**: Ruthlessly delete old inline functions, commented-out dead code, and unreferenced legacy files. Do not leave parallel implementations alive.
- **Verify Imports**: Ensure `0` circular imports and remove unused dependencies.
- **Final Verification**: Run the full build, linter, and test suite.
- **Report**: Generate a summary reporting `Added: X | Removed: Y | Net: Z` LOC to prove the reduction of complexity.


## Real-World Example of Chunked Execution

Imagine a `UserController.ts` containing 2,500 LOC handling user creation, password hashing, database saving, email sending, and analytics logging.

**Bad Approach (Big Bang Rewrite):**
Creating `AuthService`, `EmailService`, `UserRepository`, and `AnalyticsService` all at once, moving code simultaneously, and hoping it compiles. Tests will be broken for days.

**Good Approach (Chunked Refactoring):**
1. **Chunk 1:** Extract email sending logic into `EmailService.ts`. Update `UserController` to import and call `EmailService`. Run tests. Commit.
2. **Chunk 2:** Extract password hashing into `AuthService.ts`. Update `UserController`. Run tests. Commit.
3. **Chunk 3:** Extract database saving into `UserRepository.ts`. Update `UserController`. Run tests. Commit.
4. **Chunk 4:** Extract analytics into `AnalyticsService.ts`. Update `UserController`. Run tests. Commit.

By breaking the problem down, the codebase remains continuously deployable. If `Chunk 3` introduces a bug, you rollback immediately and only lose a few minutes of work.

## Handling Shared Logic (The "Wrong-DRY" Problem)

When separating components, you may notice that `User` and `Order` both have a `createdAt` and `updatedAt` timestamp, and both validate string lengths.

**Do NOT:** Create a generic `BaseModel` that handles this for both, because `User` and `Order` belong to entirely different business domains. If the requirements for `User` change (e.g., soft deletes), you don't want to accidentally impact `Order`.

**Do:** Keep the code slightly duplicated, or use granular, domain-specific value objects. Code that changes together should live together; code that looks similar but changes for different reasons must remain separate. This is the essence of true decoupling and prevents the architecture from turning into a brittle web of unintended consequences.