"""Movement, investigation and planning tools. The game validates actions."""

import json

from agents import RunContextWrapper, function_tool

from .game_context import GameContext
from .path_planner import astar
from .types import Direction


def record_action(context: GameContext, result: str) -> str:
    """Log and draw the action, then return its full observation to the model."""
    message = result.split("\n\n", 1)[0]
    print(message)
    context.visualizer.capture(message)
    return result


@function_tool
def investigate(wrapper: RunContextWrapper[GameContext], direction: Direction) -> str:
    """Reveal one adjacent cell without moving. Direction is L, R, U, or D."""
    context = wrapper.context
    print(f"\n[TOOL CALL] investigate(direction={direction!r})")
    return record_action(context, context.world.investigate(direction))


@function_tool
def move(wrapper: RunContextWrapper[GameContext], direction: Direction) -> str:
    """Move to an adjacent known safe cell. Direction is L, R, U, or D."""
    context = wrapper.context
    print(f"\n[TOOL CALL] move(direction={direction!r})")
    return record_action(context, context.world.move(direction))


@function_tool
def plan_return_to_start(wrapper: RunContextWrapper[GameContext]) -> str:
    """At the target, compute shortest return directions through known safe cells."""
    world = wrapper.context.world
    print("\n[TOOL CALL] plan_return_to_start()")
    if world.player != world.goal:
        return "Move onto the discovered target before planning the return."
    route = astar(world, world.player, world.start)
    if route is None:
        return "No safe route to the start exists through known cells."
    wrapper.context.visualizer.show_return_plan(route)
    return json.dumps({
        "from": world.player,
        "to": world.start,
        "steps": len(route),
        "directions": route,
    })
