"""Shared vocabulary; do not name this module agents.py (it shadows the SDK)."""

from typing import Literal

Position = tuple[int, int]
Direction = Literal["L", "R", "U", "D"]
