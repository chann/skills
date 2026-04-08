# Python Best Practices for Code Review

Patterns and anti-patterns to look for when reviewing Python code changes.

## Idiomatic Python

**Prefer:**
- List/dict/set comprehensions over manual loops for transformations
- `enumerate()` over manual index tracking
- `zip()` for parallel iteration instead of index-based access
- f-strings over `%` formatting or `.format()` (Python 3.6+)
- `pathlib.Path` over `os.path` string manipulation
- `dataclasses` or `NamedTuple` over plain dicts for structured data
- Context managers (`with`) for resource management
- `itertools` and `functools` for common functional patterns

**Avoid:**
- Mutable default arguments: `def foo(items=[])` — use `None` sentinel instead
- Bare `except:` or `except Exception:` that swallows all errors silently
- `type()` for type checking — use `isinstance()` which handles inheritance
- String concatenation in loops — use `"".join()` or list accumulation
- Global mutable state (module-level dicts/lists modified at runtime)

## Type Safety

- Type annotations on public function signatures (parameters and return types)
- `Optional[X]` or `X | None` (3.10+) where None is a valid value
- Avoid `Any` as a lazy escape hatch — narrow the type if possible
- Use `TypedDict` for dictionary shapes that are passed between functions
- `Protocol` classes for structural typing instead of ABC when behavior is the contract

## Error Handling

- Catch specific exceptions, not broad `Exception` or `BaseException`
- Use `raise ... from err` to preserve the exception chain
- Custom exception classes for domain errors (not generic `ValueError` for everything)
- Don't use exceptions for flow control in performance-critical paths
- `finally` or context managers for cleanup, not bare try/except

## Async Patterns

- Never mix `asyncio` and blocking I/O in the same event loop without `run_in_executor()`
- Missing `await` on coroutines — returns a coroutine object instead of the result
- `asyncio.gather()` for concurrent operations instead of sequential `await`s
- Proper cancellation handling with `asyncio.CancelledError`
- `async with` for async context managers (database connections, HTTP sessions)

## Django Specific

- N+1 queries: accessing related objects in a loop without `select_related()` / `prefetch_related()`
- Unvalidated `.get()` parameters used in querysets (SQL injection via extra/raw)
- Missing `@login_required` or permission checks on views
- `Model.objects.all()` without pagination in views serving user requests
- Using `exclude()` for authorization instead of filtering by user ownership
- Form/serializer validation bypassed by saving model directly from request data
- Missing database migrations for model changes

## FastAPI Specific

- Missing `Depends()` for shared logic (auth, DB sessions) — copy-pasted instead
- Pydantic models without proper validation constraints (`Field(ge=0)`, `constr(max_length=)`)
- Background tasks that need database sessions but the session was already closed
- Missing response model that causes entire ORM objects to be serialized (data leak)
- Synchronous I/O in async endpoints without thread pool delegation

## Testing

- `assert` statements without descriptive messages in test methods
- Mocking at the wrong level (mocking internals instead of boundaries)
- Tests that depend on execution order or shared mutable state
- Missing edge cases: empty inputs, None, boundary values, Unicode, very large inputs
- `@pytest.fixture` scope too broad (session/module when function is appropriate)
- Hardcoded dates/times instead of freezing time with `freezegun` or `time-machine`

## Performance

- Quadratic behavior: nested loops over the same collection, repeated `list.index()` or `in` on lists
- Building large strings with `+=` in a loop — O(n²) in CPython
- Loading entire file into memory when streaming/chunked processing is possible
- Missing database indexes for fields used in frequent `filter()` calls
- `copy.deepcopy()` in hot paths — consider if shallow copy or immutability works
- Regex compiled inside a loop instead of pre-compiled at module level

## Security (Python-specific)

- `pickle.loads()` on untrusted data — arbitrary code execution
- `yaml.load()` without `Loader=yaml.SafeLoader`
- `eval()` or `exec()` with any user-influenced input
- `subprocess.run(shell=True)` with user input — command injection
- `os.system()` — prefer `subprocess.run()` with explicit argument lists
- `tempfile.mktemp()` — race condition, use `tempfile.mkstemp()` or `NamedTemporaryFile`
- Format string attacks: `str.format()` with user-controlled format strings
