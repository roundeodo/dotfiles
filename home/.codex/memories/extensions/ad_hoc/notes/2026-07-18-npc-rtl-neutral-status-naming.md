# NPC RTL neutral status naming

Use neutral factual state names for NPC RTL status bits.

- Prefer `_present` for whether an object or selection currently exists.
- Prefer `_occurred` for whether an event happened previously.
- Avoid question-like `is_*` names when a neutral state noun is clearer.
- Avoid `success`, `failed`, and `done` unless the signal explicitly carries that
  architectural result.

Example: use `read_slave_selection_present`, not `read_addr_is_mapped`.
