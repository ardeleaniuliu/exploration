"""Game rules and observations, independent of the SDK and renderer."""

import random

from .cell import Cell
from .config import COLS, ROWS, SEED
from .types import Direction, Position


class GridWorld:
    """Reveal adjacent cells and move through known cells. Coordinates are (row, col)."""

    def __init__(self, rows: int = ROWS, cols: int = COLS, seed: int = SEED):
        if rows < 1 or cols < 1:
            raise ValueError("Grid dimensions must be positive.")
        self.rows = rows
        self.cols = cols
        self.random = random.Random(seed)
        self.grid: dict[Position, Cell] = {}
        self.known: set[Position] = set()
        self.player: Position = (0, 0)
        self.turn = 0
        self._generate_world()
        self._reveal(self.player)

    def _generate_world(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                roll = self.random.random()
                if roll < 0.70:
                    terrain = "grass"
                    grass_quality = self.random.uniform(0.5, 1.0)
                elif roll < 0.85:
                    terrain = "forest"
                    grass_quality = self.random.uniform(0.2, 0.6)
                else:
                    terrain = "water"
                    grass_quality = 0.0
                self.grid[(r, c)] = Cell(
                    terrain=terrain,
                    grass_quality=grass_quality,
                    wolf=self.random.random() < 0.08,
                )
        self.grid[(0, 0)] = Cell("grass", 1.0, False)

    def investigate(self, direction: Direction) -> str:
        target = self._adjacent(self.player, direction)
        if target is None:
            return self._format_result(f"INVESTIGATE {direction}: outside the grid.")
        if target in self.known:
            return self._format_result(
                f"INVESTIGATE {direction}: that cell is already known."
            )
        self._reveal(target)
        self.turn += 1
        result = (
            f"INVESTIGATE {direction}: revealed cell {target}. "
            f"{self._cell_description(target)}"
        )
        return self._format_result(result)

    def move(self, direction: Direction) -> str:
        target = self._adjacent(self.player, direction)
        if target is None:
            return self._format_result(f"MOVE {direction}: outside the grid.")
        if target not in self.known:
            return self._format_result(
                f"MOVE {direction}: that cell is unknown. Investigate it first."
            )
        self.player = target
        self.turn += 1
        result = (
            f"MOVE {direction}: moved to {target}. {self._cell_description(target)}"
        )
        return self._format_result(result)

    def observation(self) -> str:
        lines = [
            f"TURN: {self.turn}",
            f"PLAYER: row={self.player[0]}, col={self.player[1]}",
            f"KNOWN_CELLS: {len(self.known)}/{self.rows * self.cols}",
            f"EXPLORATION_COMPLETE: {self.exploration_complete}",
            "",
            "MAP:",
            "  ? = unknown, P = player, G = grass, F = forest, W = water",
        ]
        for r in range(self.rows):
            row_tokens = []
            for c in range(self.cols):
                pos = (r, c)
                if pos == self.player:
                    token = "P"
                elif pos not in self.known:
                    token = "?"
                else:
                    token = {"grass": "G", "forest": "F", "water": "W"}[
                        self.grid[pos].terrain
                    ]
                row_tokens.append(token)
            lines.append(" ".join(row_tokens))
        lines.append("")
        lines.append("KNOWN CELL DETAILS:")
        for pos in sorted(self.known):
            lines.append(f"  {pos}: {self._cell_description(pos)}")
        return "\n".join(lines)

    @property
    def exploration_complete(self) -> bool:
        return len(self.known) == self.rows * self.cols

    def _format_result(self, message: str) -> str:
        return f"{message}\n\n{self.observation()}"

    def _cell_description(self, pos: Position) -> str:
        cell = self.grid[pos]
        return (
            f"terrain={cell.terrain}, grass_quality={cell.grass_quality:.2f}, "
            f"wolf={'YES' if cell.wolf else 'no'}"
        )

    def _reveal(self, pos: Position) -> None:
        if self._in_bounds(pos):
            self.known.add(pos)

    def _in_bounds(self, pos: Position) -> bool:
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def _adjacent(self, pos: Position, direction: Direction) -> Position | None:
        if direction not in ("L", "R", "U", "D"):
            raise ValueError("Direction must be L, R, U, or D.")
        r, c = pos
        dr, dc = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}[direction]
        target = (r + dr, c + dc)
        return target if self._in_bounds(target) else None
