# JavaScript / TypeScript Best Practices for Code Review

Patterns and anti-patterns to look for when reviewing JS/TS code changes.

## Modern JavaScript

**Prefer:**
- `const` by default, `let` only when reassignment is needed — never `var`
- Arrow functions for callbacks and short functions; named functions for top-level declarations
- Template literals over string concatenation
- Optional chaining (`?.`) and nullish coalescing (`??`) over verbose null checks
- Destructuring for extracting properties from objects and arrays
- `Array.prototype` methods (`map`, `filter`, `reduce`, `find`) over manual loops for transformations
- `for...of` over `for...in` for arrays (avoids iterating prototype properties)
- `Object.entries()`, `Object.keys()`, `Object.values()` for object iteration

**Avoid:**
- `==` for comparison — use `===` to avoid type coercion surprises
- Implicit type coercion in conditionals (`if (arr.length)` is fine, but `if (count)` can hide zero-vs-falsy bugs)
- `arguments` object — use rest parameters (`...args`) instead
- `with` statement, `eval()`, `new Function()` with dynamic strings
- Modifying built-in prototypes (`Array.prototype.custom = ...`)

## TypeScript Type Safety

- Avoid `any` — use `unknown` for truly unknown types, then narrow with type guards
- Prefer `interface` for object shapes, `type` for unions and utility types
- Use discriminated unions over optional fields for variants: `{ type: "success", data } | { type: "error", error }`
- Generic constraints: `<T extends Base>` instead of unconstrained `<T>`
- `as const` for literal types and exhaustive switch/match patterns
- Non-null assertion `!` should be rare — prefer null checks or optional chaining
- `satisfies` operator (TS 4.9+) for type validation without widening
- Index signatures (`[key: string]: T`) lose type safety — prefer `Map<K, V>` or `Record<K, V>`
- Avoid type assertions (`as Type`) when type guards or narrowing would work

## Async Patterns

- Every `async` function should have error handling or the caller should catch
- Missing `await` on promises — especially in `try/catch` blocks where the catch won't fire
- `Promise.all()` for concurrent independent operations instead of sequential `await`s
- Proper cleanup: `AbortController` for fetch, `clearTimeout`/`clearInterval`, unsubscribe
- Avoid mixing callbacks and promises in the same flow
- `for await...of` for async iterables instead of manual async iteration
- Unhandled promise rejections: ensure `.catch()` or try/catch for every promise chain

## React Specific

**Hooks rules:**
- Hooks called conditionally or inside loops — must be top-level and unconditional
- Missing dependencies in `useEffect` / `useMemo` / `useCallback` dependency arrays
- Over-using `useMemo` / `useCallback` where the computation is trivial (premature optimization)
- `useEffect` that should be an event handler (runs on render instead of on action)
- Missing cleanup function in `useEffect` for subscriptions, timers, or event listeners

**Component patterns:**
- Prop drilling through many layers — consider context or composition
- Inline object/array literals as props (creates new reference every render, breaking memoization)
- Direct DOM manipulation (`document.querySelector`) instead of refs
- `key` prop missing or using array index as key for dynamic lists
- Large components (>200 lines) — consider splitting into smaller focused components
- State that could be derived from other state or props

**State management:**
- Storing derived data in state instead of computing it
- Multiple `useState` calls that always update together — consider `useReducer` or a single object
- State updates that don't use the function form when depending on previous state: `setCount(count + 1)` → `setCount(c => c + 1)`

## Node.js Specific

- Blocking the event loop with synchronous I/O (`fs.readFileSync` in request handlers)
- Unhandled `error` events on streams (crashes the process)
- Memory leaks from event listeners not being removed
- `process.env` access scattered everywhere — centralize config validation at startup
- Missing error handling middleware in Express/Fastify
- `Buffer` handling: use `Buffer.from()` not `new Buffer()` (deprecated)
- Child process spawning with `shell: true` and user input — command injection

## Error Handling

- Catching errors without re-throwing or handling: `catch (e) { /* nothing */ }`
- Throwing strings instead of Error objects: `throw "failed"` → `throw new Error("failed")`
- Error boundaries missing in React component trees for graceful failure
- Custom error classes extending `Error` should set `name` property and preserve stack
- API error responses should use consistent structure and appropriate HTTP status codes

## Testing

- Missing `beforeEach` cleanup — tests share state and become order-dependent
- Testing implementation details (internal state, private methods) instead of behavior
- Snapshot tests overused — they pass by default and rarely catch real bugs
- Mocking modules without verifying the mock matches the real interface
- Async tests without proper `await` or `done()` callback — they pass vacuously
- No integration tests for API endpoints — unit tests alone miss wiring issues

## Performance

- Bundle size: importing entire libraries when tree-shakeable named imports exist (`import _ from "lodash"` → `import { debounce } from "lodash"`)
- Unnecessary re-renders: components re-rendering because parent state changed but props didn't
- Large lists without virtualization (rendering thousands of DOM nodes)
- Synchronous JSON parsing of large payloads on the main thread
- Missing `loading` / `Suspense` boundaries for code-split components
- Event listeners on `window`/`document` without passive option where applicable

## Security (JS/TS-specific)

- `innerHTML` / `dangerouslySetInnerHTML` with user-controlled content — XSS
- `eval()`, `new Function()`, `setTimeout(string)` with dynamic input
- `window.location` manipulation from user input — open redirect
- CORS headers set to `*` on endpoints that return user-specific data
- JWT stored in `localStorage` (accessible to XSS) — `httpOnly` cookies are safer
- Missing `Content-Security-Policy` headers
- Prototype pollution via `Object.assign()` or spread with user-controlled keys (`__proto__`, `constructor`)
- Regular expressions with user input without escaping — ReDoS risk
