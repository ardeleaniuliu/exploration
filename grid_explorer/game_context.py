"""Local dependencies passed to SDK tools, rather than global variables."""

from dataclasses import dataclass

from .grid_world import GridWorld
from .world_visualizer import WorldVisualizer


@dataclass
class GameContext:
    world: GridWorld
    visualizer: WorldVisualizer
