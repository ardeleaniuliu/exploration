"""Capture game states and export an animated GIF without a GUI."""

from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

from .config import FRAME_DURATION_MS, GIF_PATH
from .grid_world import GridWorld
from .types import Direction, Position


class WorldVisualizer:
    """Builds one Matplotlib image per state; no live window is used."""

    def __init__(self, game: GridWorld):
        self.game = game
        self.frames: list[Image.Image] = []
        self.planned_path: list[Position] = []
        self.actual_path: list[Position] = []

    def show_return_plan(self, directions: list[Direction]) -> None:
        """Snapshot this plan; subsequent captures track actual movement separately."""
        pos = self.game.player
        self.planned_path = [pos]
        offsets = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}
        for direction in directions:
            dr, dc = offsets[direction]
            pos = (pos[0] + dr, pos[1] + dc)
            self.planned_path.append(pos)
        self.actual_path = [self.game.player]
        self.capture(f"A* return plan: {len(directions)} moves")

    @property
    def follows_plan(self) -> bool:
        return bool(self.planned_path) and (
            self.actual_path == self.planned_path[:len(self.actual_path)]
        )

    def capture(self, action_text: str = "Initial state") -> None:
        game = self.game
        if self.planned_path and self.actual_path[-1] != game.player:
            self.actual_path.append(game.player)
        fig, ax = plt.subplots(figsize=(7, 7))
        for r in range(game.rows):
            for c in range(game.cols):
                pos = (r, c)
                cell = game.grid[pos]
                if pos not in game.known:
                    facecolor = "lightgray"
                    label = "?"
                elif pos == game.goal:
                    facecolor = "gold"
                    label = "T"
                elif cell.terrain == "grass":
                    facecolor = "palegreen"
                    label = f"{cell.grass_quality:.1f}"
                elif cell.terrain == "forest":
                    facecolor = "darkseagreen"
                    label = "F"
                else:
                    facecolor = "lightblue"
                    label = "W"
                ax.add_patch(
                    Rectangle(
                        (c, game.rows - 1 - r),
                        1,
                        1,
                        facecolor=facecolor,
                        edgecolor="black",
                        linewidth=1,
                    )
                )
                if pos in game.known:
                    if pos == game.start:
                        label = "S"
                    elif pos == game.goal:
                        label = "T"
                    ax.text(
                        c + 0.5,
                        game.rows - 1 - r + 0.5,
                        label,
                        ha="center",
                        va="center",
                        fontsize=10,
                    )
                    if cell.wolf:
                        ax.text(
                            c + 0.5,
                            game.rows - 1 - r + 0.18,
                            "WOLF",
                            ha="center",
                            va="center",
                            fontsize=6,
                            fontweight="bold",
                        )
        if self.planned_path:
            for path, color, style, width, label in (
                (self.planned_path, "royalblue", "--", 5, "A* suggested route"),
                (self.actual_path, "darkorange", "-", 2, "Actual return movement"),
            ):
                ax.plot(
                    [c + 0.5 for r, c in path],
                    [game.rows - 1 - r + 0.5 for r, c in path],
                    color=color, linestyle=style, linewidth=width,
                    marker="o", markersize=4, label=label, zorder=2,
                )
            for step, (r, c) in enumerate(self.planned_path):
                ax.text(c + 0.12, game.rows - 1 - r + 0.85, str(step),
                        color="navy", fontsize=8, fontweight="bold")
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), fontsize=9)
        pr, pc = game.player
        ax.text(
            pc + 0.5,
            game.rows - 1 - pr + 0.78,
            "P",
            ha="center",
            va="center",
            fontsize=16,
            fontweight="bold",
        )
        ax.set_xlim(0, game.cols)
        ax.set_ylim(0, game.rows)
        ax.set_aspect("equal")
        ax.set_xticks(range(game.cols + 1))
        ax.set_yticks(range(game.rows + 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(True, linewidth=1)
        ax.set_title(
            f"Turn {game.turn} | Known {len(game.known)}/{game.rows * game.cols}\n"
            f"{action_text}"
        )
        if self.planned_path:
            comparison = "Following plan" if self.follows_plan else "Deviated from plan"
            ax.set_title(
                ax.get_title() + "\n" + comparison
                + f" | Actual moves: {len(self.actual_path) - 1}"
                + f" | Planned: {len(self.planned_path) - 1}"
            )
        fig.tight_layout()
        # Convert the Matplotlib canvas to a PIL image and retain it in memory.
        buffer = BytesIO()
        fig.savefig(buffer, format="png", dpi=100)
        buffer.seek(0)
        frame = Image.open(buffer).convert("RGB").copy()
        self.frames.append(frame)
        buffer.close()
        plt.close(fig)

    def save_gif(self, path: Path = GIF_PATH) -> None:
        if not self.frames:
            raise RuntimeError("No frames have been captured.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Add a final hold frame so the final state is easier to inspect.
        final = self.frames[-1]
        frames = self.frames + [final.copy(), final.copy()]
        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:],
            duration=FRAME_DURATION_MS,
            loop=0,
            optimize=False,
        )
