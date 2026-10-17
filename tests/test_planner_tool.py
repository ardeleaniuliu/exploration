"""Offline checks of the registered tool and movement execution."""

import json
import unittest

from agents.tool_context import ToolContext

from grid_explorer.cell import Cell
from grid_explorer.explorer_agent import create_explorer_agent
from grid_explorer.game_context import GameContext
from grid_explorer.grid_world import GridWorld
from grid_explorer.tools import move, plan_return_to_start
from grid_explorer.world_visualizer import WorldVisualizer


class PlannerToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_plan_then_execute_return(self):
        world = GridWorld(rows=2, cols=2)
        world.goal = (0, 1)
        world.grid[world.goal] = Cell("forest", 0.5)
        visualizer = WorldVisualizer(world)
        wrapper = ToolContext(
            context=GameContext(world, visualizer),
            tool_name="plan_return_to_start",
            tool_call_id="test-plan",
            tool_arguments="{}",
        )
        rejected = await plan_return_to_start.on_invoke_tool(wrapper, json.dumps({"stated_reason": "Plan the return home."}))
        self.assertIn("Move onto", rejected)
        self.assertEqual(visualizer.planned_path, [])
        world.investigate("R")
        world.move("R")
        plan = json.loads(await plan_return_to_start.on_invoke_tool(wrapper, json.dumps({"stated_reason": "Plan the return home."})))
        self.assertEqual(plan["directions"], ["L"])
        self.assertEqual(plan["steps"], 1)
        self.assertEqual(world.player, world.goal)
        self.assertEqual(world.turn, 2)
        self.assertEqual(visualizer.planned_path, [(0, 1), (0, 0)])
        self.assertEqual(visualizer.actual_path, [(0, 1)])
        self.assertEqual(len(visualizer.frames), 1)
        for direction in plan["directions"]:
            arguments = json.dumps({"direction": direction, "stated_reason": "Follow the return plan."})
            movement_context = ToolContext(
                context=wrapper.context,
                tool_name="move",
                tool_call_id="test-move",
                tool_arguments=arguments,
            )
            await move.on_invoke_tool(movement_context, arguments)
        self.assertTrue(world.mission_complete)
        self.assertEqual(visualizer.actual_path, visualizer.planned_path)
        self.assertTrue(visualizer.follows_plan)
        self.assertEqual(len(visualizer.frames), 2)

    def test_deviation_remains_visible_after_rejoining(self):
        world = GridWorld(rows=2, cols=2)
        world.grid = {pos: Cell("grass", 1.0) for pos in world.grid}
        world.known = set(world.grid)
        world.goal = (0, 1)
        world.move("R")
        visualizer = WorldVisualizer(world)
        visualizer.show_return_plan(["L"])
        world.move("D")
        visualizer.capture()
        self.assertFalse(visualizer.follows_plan)
        world.move("U")
        visualizer.capture()
        world.move("L")
        visualizer.capture()
        self.assertFalse(visualizer.follows_plan)
        self.assertEqual(visualizer.planned_path, [(0, 1), (0, 0)])
        self.assertEqual(len(visualizer.actual_path) - 1, 3)
        world.move("U")  # Rejected movement must not add a trail step.
        visualizer.capture()
        self.assertEqual(len(visualizer.actual_path) - 1, 3)

    def test_planner_is_registered(self):
        agent = create_explorer_agent()
        self.assertIn("plan_return_to_start", [tool.name for tool in agent.tools])
