"""Offline regression checks for the rules and rendering; no API key needed."""

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from grid_explorer.grid_world import GridWorld
from grid_explorer.world_visualizer import WorldVisualizer


class GridWorldTests(unittest.TestCase):
    def test_same_seed_produces_same_world(self):
        self.assertEqual(GridWorld(seed=42).grid, GridWorld(seed=42).grid)

    def test_unknown_cell_cannot_be_entered(self):
        world = GridWorld(rows=2, cols=2)
        self.assertIn("unknown", world.move("R"))
        self.assertEqual(world.player, (0, 0))
        self.assertEqual(world.turn, 0)

    def test_reveal_then_move_and_complete(self):
        world = GridWorld(rows=2, cols=2)
        world.investigate("R")
        world.move("R")
        world.investigate("D")
        world.move("D")
        world.investigate("L")
        self.assertTrue(world.exploration_complete)
        self.assertEqual(world.turn, 5)

    def test_rejected_actions_do_not_change_state(self):
        world = GridWorld(rows=2, cols=2)
        world.investigate("R")
        world.investigate("R")
        world.investigate("U")
        world.move("L")
        self.assertEqual(world.turn, 1)
        self.assertEqual(world.known, {(0, 0), (0, 1)})

    def test_observation_hides_unknown_contents(self):
        world = GridWorld(rows=2, cols=2)
        details = world.observation().split("KNOWN CELL DETAILS:")[1]
        self.assertNotIn("(0, 1)", details)
        self.assertEqual(details.count("terrain="), 1)

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            GridWorld(rows=0)
        with self.assertRaises(ValueError):
            GridWorld().move("N")

    def test_gif_export_contains_multiple_states(self):
        world = GridWorld(rows=2, cols=2)
        visualizer = WorldVisualizer(world)
        visualizer.capture()
        world.investigate("R")
        visualizer.capture("Investigate right")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested" / "run.gif"
            visualizer.save_gif(path)
            with Image.open(path) as gif:
                self.assertEqual(gif.format, "GIF")
                self.assertGreaterEqual(gif.n_frames, 2)


if __name__ == "__main__":
    unittest.main()
