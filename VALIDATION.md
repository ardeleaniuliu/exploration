# Validation

- Seven offline rule/rendering regression tests passed.
- Agent construction succeeded using the installed OpenAI Agents SDK.
- Both tool schemas expose only the direction argument, with L/R/U/D enum values.
- The actual SDK tool wrapper successfully invoked investigate with local context.
- A simulated SDK failure returned status 1 and saved a partial GIF.
- Ruff formatting and lint checks passed.
- No live model calls were made. Model availability, account permissions and
  autonomous exploration quality have not been verified.
