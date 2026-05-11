# Samples — intentionally vulnerable fixtures

These files exist so the `code-review` skill has obvious findings to demonstrate
during development and demos. **None of this code is meant to be deployed.**
Every file in this folder is deliberately broken; SAST tools that flag them are
correct.

## Contents

```
samples/
└── code-review/
    ├── python-auth/auth_service.py    # SQL injection, MD5, pickle, os.system, hardcoded secret
    ├── react-dashboard/Dashboard.tsx  # Hardcoded API key, dangerouslySetInnerHTML XSS, hook misuse
    └── go-api/handler.go              # SQL injection, password leak in responses, CORS wildcard
```

## Why they live here, not inside `code-review/`

When the samples lived under `code-review/samples/`, Snyk and other SAST tools
scanned them as part of the published plugin artifact and reported the
plugin as High Risk. The samples are now outside every plugin folder so they
don't ship in the published artifact, and `.snyk` policy files at the repo
root and inside `code-review/` add belt-and-suspenders by telling scanners to
skip them.

## Using them

Point the `code-review` skill at one of these files to see what it flags:

```
> /code-review-md review samples/code-review/python-auth/auth_service.py
```

The skill should produce a report with CRITICAL/HIGH findings for SQL
injection, weak crypto, insecure deserialization, etc.

## DO NOT

- Copy these files into a real codebase.
- Treat them as a how-to.
- File security reports against them — they exist precisely to be vulnerable.
