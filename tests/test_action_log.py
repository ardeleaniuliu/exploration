"""Check actual tool transitions, persistence, and hidden-state boundaries offline."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from agents.tool_context import ToolContext

from grid_explorer.action_log import ActionLog
from grid_explorer.game_context import GameContext
from grid_explorer.grid_world import GridWorld
from grid_explorer.tools import investigate, move, plan_return_to_start


class ActionLogTests(unittest.IsolatedAsyncioTestCase):
    async def test_tools_record_observations_and_rejections(self):
        with tempfile.TemporaryDirectory() as directory:
            log = ActionLog(Path(directory))
            world = GridWorld(rows=2, cols=2)
            context = GameContext(world, Mock(), log)
            initial = world.observation()
            actions = [
                (move, {"direction": "L", "stated_reason": "Try moving left."}),
                (investigate, {"direction": "R", "stated_reason": "Reveal the unknown neighbor."}),
                (plan_return_to_start, {"stated_reason": "Find a route home."}),
            ]
            for tool, args in actions:
                wrapper = ToolContext(context=context, tool_name=tool.name,
                                      tool_call_id="test", tool_arguments=json.dumps(args))
                await tool.on_invoke_tool(wrapper, json.dumps(args))
            records = [json.loads(line) for line in log.path.read_text().splitlines()]
            self.assertEqual(len(records), 3)
            self.assertEqual(records[0]["state_before"], initial)
            self.assertIn("GOAL: unknown", records[0]["state_before"])
            self.assertNotIn("  (0, 1): terrain=", records[0]["state_before"])
            self.assertEqual(records[0]["state_after"], initial)
            self.assertIn("outside the grid", records[0]["result"])
            self.assertEqual(records[1]["state_before"], initial)
            self.assertNotEqual(records[1]["state_after"], initial)
            self.assertEqual(records[1]["stated_reason"], actions[1][1]["stated_reason"])
            self.assertEqual(records[2]["state_before"], records[1]["state_after"])
            self.assertEqual(records[2]["state_after"], world.observation())
            self.assertEqual([record["step"] for record in records], [1, 2, 3])
            self.assertNotEqual(ActionLog(Path(directory)).path, log.path)
