"""The two actions the model can request. The game validates each action."""

from agents import RunContextWrapper, function_tool

from .game_context import GameContext
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
    """Move to an adjacent known cell. Direction is L, R, U, or D."""
    context = wrapper.context
    print(f"\n[TOOL CALL] move(direction={direction!r})")
    return record_action(context, context.world.move(direction))
