# ZCode Real-World Training Project Rules

## Goal

This is a small training repository used to demonstrate how an engineering Agent enters an existing project, reproduces a failure, makes a minimal fix, verifies it, and reviews the resulting diff.

## Working rules

- Read existing tests before changing implementation.
- Reproduce the reported failure before editing code.
- Prefer the smallest correct change.
- Do not rename public functions.
- Do not change tests only to make them pass.
- Do not add third-party dependencies.
- Avoid unrelated refactors.

## Verification

Before declaring the task complete, run:

```bash
python -m unittest discover -s tests -v
```

All tests must pass.

## Delivery

Report:

1. the root cause;
2. the file changed;
3. the verification command and result;
4. anything not verified.
