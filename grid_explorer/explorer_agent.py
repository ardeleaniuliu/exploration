"""Build the agent separately from the game and application lifecycle."""

from agents import Agent, ModelSettings
from openai.types.shared import Reasoning

from .config import MODEL
from .game_context import GameContext
from .tools import investigate, move

INSTRUCTIONS = """
You are an autonomous explorer.
Your goal is to reveal the entire grid.
You initially know only your current cell.

Actions:
- investigate(direction): reveal one adjacent cell without moving.
- move(direction): move into an adjacent cell that is already known.
- Directions: L = left, R = right, U = up, D = down.

After each action, use the returned observation to choose your next action.
Request exactly one action at a time because actions change shared game state.
Never assume the contents of unknown cells. 
Prefer revealing unknown neighbors.
When all neighbors are known, move through known cells toward an unexplored area.
Avoid investigating known cells and avoid out-of-bounds actions.
It is okay to visit known cells to reach unknown cells, but do not waste turns wandering.
Water, forest and wolves are descriptive only.
You must never visit water and wolf cells as they are dangerous.
Forest cells should only be visited if necessary to reach unknown areas.
Very importantly, don't give up early; keep exploring until the entire grid is revealed even if that means taking many turns, visiting known cells or forests.
Continue acting until EXPLORATION_COMPLETE is true, then give a brief final report.
"""


def create_explorer_agent(model: str = MODEL) -> Agent[GameContext]:
    return Agent[GameContext](
        name="Grid World Explorer",
        model=model,
        instructions=INSTRUCTIONS,
        tools=[investigate, move],
        model_settings=ModelSettings(
            reasoning=Reasoning(effort="low"),
            parallel_tool_calls=False,
        ),
    )
