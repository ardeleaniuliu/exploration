"""Experiment settings: start small while reviewing the agent's decisions."""

from pathlib import Path

ROWS = 8
COLS = 8
SEED = 42
GIF_PATH = Path("grid_world_run_6.gif")
FRAME_DURATION_MS = 300
MAX_AGENT_TURNS = 100
# Preserve the supplied model; override it with OPENAI_MODEL in .env if needed.
MODEL = "gpt-6-luna"
