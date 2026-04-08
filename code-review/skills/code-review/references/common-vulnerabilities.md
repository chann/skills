# Common Vulnerabilities Checklist

Load this reference when the diff touches security-sensitive code — authentication, authorization, cryptography, input handling, database access, file operations, or network communication.

Organized by OWASP Top 10 categories with concrete patterns to look for in code diffs.

## A01: Broken Access Control

- New API endpoint or route without authentication middleware
- Authorization check based on client-supplied data (user ID from request body instead of session)
- Missing ownership verification: user A can access user B's resources by changing an ID parameter
- CORS configured with wildcard `*` or overly permissive origins
- Directory listing enabled or sensitive paths not protected
- JWT token validation skipped or improperly implemented (e.g., `alg: none` accepted)
- Missing CSRF protection on state-changing operations

## A02: Cryptographic Failures

- Passwords stored in plaintext or with weak hashing (MD5, SHA1 without salt)
- Hardcoded encryption keys or initialization vectors
- Use of deprecated algorithms (DES, RC4, SHA1 for security purposes)
- TLS/SSL configuration with weak ciphers or disabled certificate verification
- Sensitive data transmitted without encryption
- Predictable random values used for security tokens (using `Math.random()` or `random.random()` instead of `secrets`/`crypto`)
- Missing key rotation mechanism for long-lived secrets

## A03: Injection

**SQL injection:**
- String concatenation or f-strings building SQL: `f"SELECT * FROM users WHERE id = {user_id}"`
- ORM raw queries with interpolated values instead of parameterized bindings
- Dynamic table or column names from user input

**Command injection:**
- `os.system()`, `subprocess.run(shell=True)`, `exec()` with user-controlled input
- Template strings in shell commands without proper escaping

**XSS (Cross-Site Scripting):**
- User input rendered as HTML without escaping (`innerHTML`, `dangerouslySetInnerHTML`, `|safe` filter)
- URL parameters reflected in page output
- JavaScript template literals with unsanitized user data

**Other injection vectors:**
- LDAP injection via string concatenation in queries
- XML External Entity (XXE) processing with external entities enabled
- Log injection: unsanitized user input in log messages enabling log forging
- Header injection: user input in HTTP response headers

## A04: Insecure Design

- Business logic that trusts client-side validation alone
- Rate limiting absent on expensive operations (login, password reset, API calls)
- Missing account lockout after failed authentication attempts
- Sensitive operations without re-authentication (password change, email change)
- Predictable resource identifiers (sequential IDs exposing resource count)

## A05: Security Misconfiguration

- Debug mode enabled in production configuration
- Default credentials or example secrets left in config files
- Error responses that reveal stack traces, SQL queries, or internal paths
- Unnecessary features, ports, or services enabled
- Security headers missing (CSP, X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security)
- Overly permissive file upload (no type validation, no size limit, executable extensions allowed)

## A06: Vulnerable and Outdated Components

- Dependencies with known CVEs (check version against advisory databases)
- Unmaintained packages (no updates in >2 years, archived repositories)
- Importing a heavy library for a trivial function that stdlib can handle
- Lock file changes that downgrade a dependency version

## A07: Identification and Authentication Failures

- Session tokens that don't rotate after login
- Session fixation: accepting session IDs from URL parameters
- Missing session timeout or overly long session lifetime
- Password reset tokens that don't expire or are reusable
- Multi-factor authentication bypass paths
- User enumeration through different error messages for valid vs invalid usernames

## A08: Software and Data Integrity Failures

- Deserialization of untrusted data: `pickle.loads()`, `yaml.unsafe_load()`, Java `ObjectInputStream`
- CI/CD pipeline modifications without review (workflow files, Dockerfiles)
- Missing integrity checks on downloaded resources or auto-updates
- Code or data loaded from CDN without Subresource Integrity (SRI) hashes

## A09: Security Logging and Monitoring Failures

- Security-relevant events not logged (login failures, access denied, privilege changes)
- Log injection possible (user input in log messages without sanitization)
- Sensitive data in logs (tokens, passwords, credit card numbers, PII)
- Logging to insecure destinations or without log integrity protection

## A10: Server-Side Request Forgery (SSRF)

- URL fetching where the target URL comes from user input without allowlist validation
- Internal service URLs constructable by manipulating request parameters
- DNS rebinding not considered when validating URLs
- Redirect following that could reach internal networks
