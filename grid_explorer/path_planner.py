"""A* shortest paths through revealed, safe cells; every move costs one."""

from heapq import heappop, heappush

from .grid_world import GridWorld
from .types import Direction, Position


def astar(
    world: GridWorld, start: Position, destination: Position
) -> list[Direction] | None | str:
    """Return movement directions, or None if no known safe route exists."""
    if not world.is_walkable(start) or not world.is_walkable(destination):
        return None
    
    def heuristic(pos: Position) -> int:
        return abs(pos[0] - destination[0]) + abs(pos[1] - destination[1])

    frontier = [(heuristic(start), 0, start)]
    costs = {start: 0}
    parents: dict[Position, tuple[Position, Direction]] = {}
    offsets: dict[Direction, Position] = {
        "L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)
    }

    while frontier:
        _, cost, current = heappop(frontier)
        if cost != costs[current]:
            continue
        if current == destination:
            route: list[Direction] = []
            while current != start:
                previous, direction = parents[current]
                route.append(direction)
                current = previous
            return route[::-1]

        for direction, (dr, dc) in offsets.items():
            neighbor = (current[0] + dr, current[1] + dc)
            if not world.is_walkable(neighbor):
                continue
            new_cost = cost + 1
            if new_cost < costs.get(neighbor, float("inf")):
                costs[neighbor] = new_cost
                parents[neighbor] = (current, direction)
                heappush(frontier, (new_cost + heuristic(neighbor), new_cost, neighbor))

    return None
