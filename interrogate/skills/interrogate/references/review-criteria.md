# Review Criteria Framework

Use this document as a reference when analyzing code changes. Each dimension lists concrete patterns to look for — not an exhaustive checklist, but a guide to focus attention on the things that matter most in real-world code reviews.

## 1. Correctness

The code should do what the author intended, handle edge cases, and not break existing behavior.

**Logic errors:**
- Off-by-one in loops, slicing, or pagination
- Inverted or incomplete boolean conditions (`&&` vs `||`, missing negation)
- Switch/match statements without exhaustive handling or missing default/break
- Floating-point comparison with `==` instead of epsilon-based comparison
- Integer overflow or underflow in arithmetic

**Null / undefined / empty handling:**
- Dereferencing potentially null values without guards
- Empty collection assumptions (calling `.first()` on a possibly-empty list)
- Optional chaining missing where a chain of access could fail

**Async and concurrency:**
- Race conditions from shared mutable state
- Missing `await` on async calls (returns a Promise/coroutine instead of the value)
- Deadlocks from lock ordering or nested locks
- Unhandled promise rejections or swallowed exceptions in async contexts

**Error propagation:**
- Catching exceptions too broadly (`except Exception`, `catch (e)`) and silently continuing
- Errors caught but not logged or re-raised — silent failure
- Error messages that don't include enough context for debugging
- Missing cleanup in error paths (resources left open)

**Type mismatches:**
- String where number expected (or vice versa), especially in dynamically-typed languages
- Incorrect generic type parameters
- Unsafe type assertions / casts that bypass type checking

**State management:**
- Stale state after mutation (e.g., UI not re-rendering, cache not invalidated)
- Partial updates that leave data in an inconsistent state
- Missing transaction boundaries where atomicity is required

## 2. Security

Look for vulnerabilities that could be exploited. When security-sensitive files are touched, also load `common-vulnerabilities.md` for a deeper checklist.

**Injection:**
- SQL queries built with string concatenation or f-strings instead of parameterized queries
- Shell commands built from user input without escaping
- HTML output with unescaped user data (XSS)
- Template injection in server-side rendering

**Authentication & authorization:**
- Missing auth checks on new endpoints or routes
- Privilege escalation paths (user can access admin resources)
- Hardcoded credentials, API keys, or tokens
- Weak password validation or missing rate limiting on auth endpoints

**Data exposure:**
- Sensitive data in logs (passwords, tokens, PII)
- API responses that return more fields than the client needs
- Stack traces or internal error details exposed to end users
- Secrets committed in config files or environment variables

**Input validation:**
- Missing validation at system boundaries (API inputs, file uploads, webhook payloads)
- Regex denial of service (ReDoS) from catastrophic backtracking patterns
- Path traversal (user-controlled file paths without sanitization)
- Deserialization of untrusted data (pickle, YAML unsafe load, Java serialization)

## 3. Complexity & Consistency

Changes should not make the codebase harder to understand or break established patterns.

**Cognitive complexity:**
- Deeply nested conditionals (>3 levels) — consider early returns or extraction
- Functions doing too many things (>30 lines is a signal, not a rule)
- Complex ternary expressions or chained boolean logic that would be clearer as named conditions

**Pattern consistency:**
- New code that uses a different style than surrounding code for the same problem (e.g., callbacks where the rest of the codebase uses async/await)
- Introducing a new utility when an equivalent already exists in the codebase
- Inconsistent naming: different conventions in the same module (camelCase mixed with snake_case)
- Different error handling strategies in the same layer

**Duplication:**
- Copy-pasted blocks with minor variations — candidate for extraction
- Parallel structures that will drift apart over time

**Abstraction level:**
- Premature abstraction: creating interfaces/generics for a single use case
- Under-abstraction: raw implementation details scattered across multiple call sites
- Leaky abstractions that expose internals to callers

## 4. Maintainability

Will the next developer who touches this code understand it and be able to change it safely?

**Readability:**
- Magic numbers or strings without named constants or explanation
- Variable names that are too short, too generic (`data`, `result`, `tmp`), or misleading
- Long parameter lists (>4-5 parameters — consider a config object)

**Testability:**
- New logic without corresponding tests
- Tight coupling that makes unit testing impossible without extensive mocking
- Hidden dependencies (global state, singletons, implicit service locators)
- Non-deterministic behavior that makes tests flaky

**Documentation:**
- Public APIs (exported functions, REST endpoints) without doc comments
- Complex business logic without explaining the "why"
- Outdated comments that contradict the current code

**Separation of concerns:**
- Business logic mixed with I/O, presentation, or framework plumbing
- Database queries embedded in controller/handler code
- Configuration mixed with runtime logic

**Dependency management:**
- New dependencies added for trivial functionality (can stdlib do this?)
- Pinning to exact versions vs using ranges — appropriate for the ecosystem?
- Dependencies with known vulnerabilities or unmaintained status

## 5. Best Practices

Language and framework-specific idioms. Defer to the relevant `references/<language>.md` file for detailed patterns. At a high level:

- Use the language's built-in constructs over manual reimplementations
- Follow the ecosystem's conventions for project structure, naming, and error handling
- Use framework features as intended (don't fight the framework)
- Prefer immutability where the language supports it
- Handle resources properly (close files, release connections, cancel subscriptions)
