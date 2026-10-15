"""Data stored in a single map cell."""

from dataclasses import dataclass


@dataclass
class Cell:
    terrain: str
    grass_quality: float
    wolf: bool = False
