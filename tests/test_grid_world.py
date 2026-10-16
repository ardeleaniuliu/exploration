"""Offline regression checks for the rules and rendering; no API key needed."""

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from grid_explorer.cell import Cell
from grid_explorer.grid_world import GridWorld
from grid_explorer.path_planner import astar
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
        world.grid = {pos: Cell("grass", 1.0) for pos in world.grid}
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

    def test_goal_is_deterministic_and_reachable(self):
        world = GridWorld()
        self.assertEqual(world.goal, GridWorld().goal)
        self.assertNotEqual(world.goal, world.start)
        world.known = set(world.grid)
        self.assertIsNotNone(astar(world, world.start, world.goal))

    def test_no_possible_goal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "No reachable target"):
            GridWorld(rows=1, cols=1)

    def test_discovery_visit_and_return_are_distinct(self):
        world = GridWorld(rows=2, cols=2)
        world.grid[(0, 1)] = Cell("forest", 0.5)
        world.goal = (0, 1)
        self.assertIn("GOAL: unknown", world.observation())
        self.assertFalse(world.mission_complete)
        world.investigate("R")
        self.assertIn("GOAL: (0, 1)", world.observation())
        self.assertFalse(world.goal_visited)
        world.move("R")
        self.assertTrue(world.goal_visited)
        self.assertFalse(world.mission_complete)
        route = astar(world, world.player, world.start)
        self.assertEqual(route, ["L"])
        for direction in route:
            world.move(direction)
        self.assertTrue(world.mission_complete)
        self.assertFalse(world.exploration_complete)

    def test_hazardous_moves_do_not_change_state(self):
        for cell in (Cell("water", 0.0), Cell("forest", 0.5, True)):
            with self.subTest(cell=cell):
                world = GridWorld(rows=2, cols=2)
                world.grid[(0, 1)] = cell
                world.investigate("R")
                self.assertIn("forbidden", world.move("R"))
                self.assertEqual(world.player, world.start)
                self.assertEqual(world.turn, 1)

    def test_astar_avoids_unknown_water_and_wolves(self):
        for blocked in ("unknown", "water", "wolf"):
            with self.subTest(blocked=blocked):
                world = GridWorld(rows=3, cols=3)
                world.grid = {pos: Cell("forest", 0.5) for pos in world.grid}
                world.known = set(world.grid)
                if blocked == "unknown":
                    world.known.remove((0, 1))
                elif blocked == "water":
                    world.grid[(0, 1)] = Cell("water", 0.0)
                else:
                    world.grid[(0, 1)].wolf = True
                before = (world.player, world.turn, world.known.copy())
                route = astar(world, (0, 0), (0, 2))
                self.assertIsNotNone(route)
                self.assertEqual(len(route), 4)
                self.assertEqual(before, (world.player, world.turn, world.known))
                for direction in route:
                    world.move(direction)
                self.assertEqual(world.player, (0, 2))
                self.assertEqual(world.turn, 4)

    def test_astar_handles_unreachable_and_identical_endpoints(self):
        world = GridWorld(rows=2, cols=2)
        world.grid = {pos: Cell("grass", 1.0) for pos in world.grid}
        self.assertEqual(astar(world, world.start, world.start), [])
        self.assertIsNone(astar(world, world.start, (1, 1)))
        world.known.add((1, 1))
        self.assertIsNone(astar(world, world.start, (1, 1)))
        world.grid[world.start].wolf = True
        self.assertIsNone(astar(world, world.start, world.start))

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
