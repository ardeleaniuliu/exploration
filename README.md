# Grid world explorer

A readable refactor of your exploration proof of concept. The model chooses
actions; Python enforces the game rules and renders the resulting states.
Each application class has its own file. A* plans the return journey through
known safe cells after the agent reaches the target.

## Target and return mission

The world chooses a non-start target reachable through grass/forest without
wolves. Its location stays hidden until investigated. Worlds with no eligible
target (including a 1x1 grid) raise a clear error; choose another seed or size.

The agent explores, moves onto the discovered target, calls
`plan_return_to_start`, and executes the returned directions using individual
`move` calls. Planning does not move the player or consume a game turn.
Unknown cells, water and wolves are blocked by A*; movement enforces the same
rule. Forest and grass both cost one step. The shortest route is relative to
the known map, not undiscovered shortcuts.

Success is `MISSION_COMPLETE`: the target was visited and the player returned
to the start. Full-grid exploration is no longer required. The GIF labels the
start `S` and the revealed target `T`.

Review `grid_world.py` for rules, `path_planner.py` for A*, `tools.py` for its
SDK wrapper, and `explorer_agent.py` for the mission instructions.

## Start here

Read `cell.py`, then `grid_world.py`, then `tools.py`, then `explorer_agent.py`,
and finally `main.py`. Read `world_visualizer.py` when you want to change the GIF.

| File | Responsibility |
| --- | --- |
| `grid_explorer/cell.py` | `Cell`: terrain, grass quality and wolf marker |
| `grid_explorer/grid_world.py` | `GridWorld`: map generation, rules and observations |
| `grid_explorer/world_visualizer.py` | `WorldVisualizer`: capture frames and export a GIF |
| `grid_explorer/game_context.py` | `GameContext`: the world and renderer for one SDK run |
| `grid_explorer/tools.py` | SDK tools: investigate, move and plan_return_to_start |
| `grid_explorer/path_planner.py` | A* through known safe cells |
| `grid_explorer/explorer_agent.py` | Agent factory, instructions and model settings |
| `grid_explorer/config.py` | Dimensions, seed, model, GIF settings and turn limit |
| `grid_explorer/types.py` | Position and direction type aliases |
| `main.py` | Setup, SDK run, error handling and final summary |
| `tests/test_grid_world.py` | Offline regression checks |

## Run on Windows / PowerShell

Use Python 3.10 or newer. Extract this project, open its folder in VS Code,
and run these commands in the terminal from the folder containing `main.py`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and replace the placeholder API key with your own key.
.\.venv\Scripts\python.exe main.py
```

The original model string `gpt-5.6-luna` is preserved. Its availability for your
API account has not been verified. If it is unavailable, set `OPENAI_MODEL` in
`.env` to a model your account can use. The selected model must support function
tools and the configured reasoning and parallel-tool settings; adjust those in
`explorer_agent.py` if needed.

The animation is saved as `grid_world_run.gif` in your current working directory.
Live runs make paid API calls. The direct dependencies are pinned to the versions used for the offline checks.

## What changed

- Split each class into a separate module with small, focused supporting modules.
- Replaced global world/visualizer variables and assertions with SDK local context.
- Moved agent creation and `.env` loading out of import-time code.
- Disabled parallel tool calls and requested one action at a time, so state updates
  are easier to follow. This changes scheduling, not the game rules.
- Save the GIF once, including partial progress after a failed SDK run.
- Avoid reading an undefined `result` after an exception.
- Report actual exploration completion and return a nonzero process status for
  errors or incomplete exploration, even if the model produces a final report.
- Validate positive grid dimensions and invalid direction values.
- Create the GIF's destination directory when necessary.
- Removed Markdown escapes and unusual whitespace from the pasted Python.
- Removed a redundant image copy during frame capture.

## Understand the experiment

Coordinates are `(row, column)`, starting at `(0, 0)` in the top-left corner.
Investigating reveals one adjacent cell but does not move the player. Moving
requires an already revealed destination. Successful actions increment
`world.turn`; rejected actions do not. A move can revisit a known cell.

`EXPLORATION_COMPLETE` still measures whether every cell is revealed, but is
only a statistic. Mission completion requires visiting the target and returning
home. Water and wolves block movement; forests are allowed. Grass quality is
descriptive and does not affect route cost.

The model sees the initial observation and tool responses, including known-cell
details. The local `GameContext` is used by Python tools and is not itself sent
to the model. A tool can access the full game internally, but observations expose
only known cells.

`MAX_AGENT_TURNS = 20` preserves your original SDK limit. SDK turns count model
iterations, not `world.turn`. A full 8x8 grid requires at least 63 successful
investigations, plus moves, so 20 is a deliberately limited trial and is unlikely
to finish with one action per iteration. Try `ROWS = COLS = 3` first, then adjust
the limit deliberately. A higher limit allows more model calls and API spend;
it does not guarantee that the model will explore efficiently or finish.

## Offline checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These check seeded generation, reveal-before-move rules, rejected actions,
completion, hidden-cell observations, input validation and GIF export. They do
not evaluate the quality of live model decisions.

## Official SDK references

- [Agents and local context](https://developers.openai.com/api/docs/guides/agents/define-agents)
- [Running agents](https://developers.openai.com/api/docs/guides/agents/running-agents)

Local context makes it possible to create independent worlds for independent
runs without swapping module globals. Keep `agents.py` out of the project root:
that name would shadow the installed `agents` package.
