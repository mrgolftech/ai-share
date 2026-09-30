# Sensor Guard Training Project

A deliberately small Python project for the AI Agent engineering training.

## Requirement

`classify_temperature(temp_c)` must classify temperature as:

| Temperature | Status |
|---|---|
| `temp_c < 75.0` | `normal` |
| `75.0 <= temp_c < 85.0` | `warning` |
| `temp_c >= 85.0` | `critical` |

## Run tests

```bash
python -m unittest discover -s tests -v
```

The initial training state intentionally contains one failing boundary-condition test.

The learner should not be told the implementation bug in advance during the live Agent demo.
