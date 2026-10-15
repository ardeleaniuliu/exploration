"""Run from this project directory with: python main.py."""

import asyncio
import os
from pathlib import Path

from agents import Runner
from dotenv import load_dotenv

from grid_explorer.config import GIF_PATH, MAX_AGENT_TURNS, MODEL
from grid_explorer.explorer_agent import create_explorer_agent
from grid_explorer.game_context import GameContext
from grid_explorer.grid_world import GridWorld
from grid_explorer.world_visualizer import WorldVisualizer


async def main() -> int:
    load_dotenv(Path(__file__).with_name(".env"))
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in your environment or in .env before running.")
        return 1

    world = GridWorld()
    visualizer = WorldVisualizer(world)
    context = GameContext(world, visualizer)
    agent = create_explorer_agent(os.getenv("OPENAI_MODEL") or MODEL)
    visualizer.capture("Initial state")
    print("Starting agent...")
    print(world.observation())
    status = 0

    try:
        result = await Runner.run(
            agent,
            f"Explore this world completely. Start acting now.\n\n{world.observation()}",
            context=context,
            max_turns=MAX_AGENT_TURNS,
        )
        print(f"\nAgent report: {result.final_output}")
    except Exception as error:  # noqa: BLE001 - log SDK/API failures at the CLI boundary.
        # Keep the partial animation, but return an unsuccessful process status.
        print(f"\nAgent stopped ({type(error).__name__}): {error}")
        status = 1
    finally:
        visualizer.save_gif(GIF_PATH)
        print(f"\nExploration complete: {world.exploration_complete}")
        print(f"Known cells: {len(world.known)}/{world.rows * world.cols}")
        print(f"Successful game actions: {world.turn}")
        print(f"GIF saved to: {GIF_PATH.resolve()}")

    # An agent's final report alone does not prove the task was completed.
    return status if world.exploration_complete else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
