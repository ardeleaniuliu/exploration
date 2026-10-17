"""Local dependencies passed to SDK tools, rather than global variables."""

from dataclasses import dataclass

from .action_log import ActionLog
from .grid_world import GridWorld
from .world_visualizer import WorldVisualizer


@dataclass
class GameContext:
    world: GridWorld
    visualizer: WorldVisualizer
    action_log: ActionLog | None = None
