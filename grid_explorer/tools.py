"""Movement, investigation and planning tools. The game validates actions."""

import json

from agents import RunContextWrapper, function_tool

from .game_context import GameContext
from .path_planner import astar
from .types import Direction


def log_transition(context: GameContext, before: str, action: dict,
                   stated_reason: str, result: str) -> None:
    if context.action_log is not None:
        context.action_log.append(
            state_before=before, action=action, stated_reason=stated_reason,
            state_after=context.world.observation(), result=result.split("\n\n", 1)[0],
        )


def record_action(context: GameContext, result: str) -> str:
    """Log and draw the action, then return its full observation to the model."""
    message = result.split("\n\n", 1)[0]
    print(message)
    context.visualizer.capture(message)
    return result


@function_tool
def investigate(wrapper: RunContextWrapper[GameContext], direction: Direction,
                stated_reason: str) -> str:
    """Reveal an adjacent cell. Supply a brief reason grounded in known state."""
    context = wrapper.context
    before = context.world.observation()
    print(f"\n[TOOL CALL] investigate(direction={direction!r})")
    result = context.world.investigate(direction)
    log_transition(context, before, {"name": "investigate", "direction": direction}, stated_reason, result)
    return record_action(context, result)


@function_tool
def move(wrapper: RunContextWrapper[GameContext], direction: Direction,
         stated_reason: str) -> str:
    """Move to a known safe neighbor. Supply a brief reason grounded in known state."""
    context = wrapper.context
    before = context.world.observation()
    print(f"\n[TOOL CALL] move(direction={direction!r})")
    result = context.world.move(direction)
    log_transition(context, before, {"name": "move", "direction": direction}, stated_reason, result)
    return record_action(context, result)


@function_tool
def plan_return_to_start(wrapper: RunContextWrapper[GameContext], stated_reason: str) -> str:
    """Plan a safe route home at the target. Supply a brief reason for planning."""
    context = wrapper.context
    before = context.world.observation()
    result = _plan_return(context)
    log_transition(context, before, {"name": "plan_return_to_start"}, stated_reason, result)
    return result


def _plan_return(context: GameContext) -> str:
    world = context.world
    print("\n[TOOL CALL] plan_return_to_start()")
    if world.player != world.goal:
        return "Move onto the discovered target before planning the return."
    route = astar(world, world.player, world.start)
    if route is None:
        return "No safe route to the start exists through known cells."
    context.visualizer.show_return_plan(route)
    return json.dumps({
        "from": world.player,
        "to": world.start,
        "steps": len(route),
        "directions": route,
    })
