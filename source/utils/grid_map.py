"""
Module providing utility map class that has methods for:
creating grid representation of maps
creating a path from point A to point B, using A* algorithm with path smoothing optimization
"""

import math
from queue import PriorityQueue
import pytmx

from source.core.settings import TILE_SIZE


class GridMap:
    def __init__(self):
        self.scale = 1
        self.scaled_tile_size = TILE_SIZE / self.scale
        self.grid = None

    def construct(self, p_map: pytmx.TiledMap):
        self.grid = [
            [0 for i in range(p_map.width * self.scale)]
            for j in range(p_map.height * self.scale)
        ]
        for obj in p_map.get_layer_by_name("Collisions"):
            grid_width = math.ceil(obj.width / self.scaled_tile_size)
            grid_height = math.ceil(obj.height / self.scaled_tile_size)
            for i in range(grid_height):
                for j in range(grid_width):
                    self.grid[int(obj.y / self.scaled_tile_size) + i][
                        int(obj.x / self.scaled_tile_size) + j
                    ] = 1
        # self.show_map()

    def show_map(self, filename="map.txt", diff_grid=None):
        used_grid = None
        if diff_grid:
            used_grid = diff_grid
        else:
            used_grid = self.grid

        with open(filename, "w", encoding="utf-8") as f:
            for rows in used_grid:
                for item in rows:
                    f.write("%d " % item)
                f.write("\n")

    def show_path(self, path):
        for point in path:
            self.grid[int(point[1] / self.scaled_tile_size)][
                int(point[0] / self.scaled_tile_size)
            ] = 5
        self.show_map("path.txt")
        for point in path:
            self.grid[int(point[1] / self.scaled_tile_size)][
                int(point[0] / self.scaled_tile_size)
            ] = 0

    def get_path(self, start_cords, goal_cords):
        def get_neighboars(point: tuple[int, int]):
            x, y = point
            valid_neigh = []

            # Orthogonal directions (Up, Down, Left, Right)
            ortho = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for nx, ny in ortho:
                if 0 <= ny < len(self.grid) and 0 <= nx < len(self.grid[0]):
                    if self.grid[ny][nx] == 0:
                        valid_neigh.append((nx, ny))

            # Diagonal directions with corner-cutting prevention
            # Format: ((target_x, target_y), (adjacent1_x, adjacent1_y), (adjacent2_x, adjacent2_y))
            diagonals = [
                ((x + 1, y + 1), (x + 1, y), (x, y + 1)),  # Bottom-Right
                ((x - 1, y - 1), (x - 1, y), (x, y - 1)),  # Top-Left
                ((x + 1, y - 1), (x + 1, y), (x, y - 1)),  # Top-Right
                ((x - 1, y + 1), (x - 1, y), (x, y + 1)),  # Bottom-Left
            ]

            for (nx, ny), (adj1_x, adj1_y), (adj2_x, adj2_y) in diagonals:
                if 0 <= ny < len(self.grid) and 0 <= nx < len(self.grid[0]):
                    if self.grid[ny][nx] == 0:
                        # Prevent clipping: Both adjacent orthogonal tiles must be walkable (0)
                        if (
                            self.grid[adj1_y][adj1_x] == 0
                            and self.grid[adj2_y][adj2_x] == 0
                        ):
                            valid_neigh.append((nx, ny))

            return valid_neigh

        def heuristic(a, b):
            # Euclidean distance on a square grid
            return math.hypot(a[0] - b[0], a[1] - b[1])
            # return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # x = col , y = row
        grid_start_x = int(start_cords[0] / self.scaled_tile_size)
        grid_start_y = int(start_cords[1] / self.scaled_tile_size)
        grid_goal_x = int(goal_cords[0] / self.scaled_tile_size)
        grid_goal_y = int(goal_cords[1] / self.scaled_tile_size)

        start = (grid_start_x, grid_start_y)
        goal = (grid_goal_x, grid_goal_y)

        p_queue = PriorityQueue()
        p_queue.put((0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        # MAP GRID
        while not p_queue.empty():
            current = p_queue.get()[1]
            if current == goal:
                break
            for next_neightboar in get_neighboars(current):
                if (
                    current[0] != next_neightboar[0]
                    and current[1] != next_neightboar[1]
                ):
                    step_cost = 1.414
                else:
                    step_cost = 1

                new_cost = cost_so_far[current] + step_cost
                if (
                    next_neightboar not in cost_so_far
                    or new_cost < cost_so_far[next_neightboar]
                ):
                    cost_so_far[next_neightboar] = new_cost
                    priority = new_cost + heuristic(next_neightboar, goal)
                    p_queue.put((priority, next_neightboar))
                    came_from[next_neightboar] = current

        # BUILD PATH
        current = goal
        path = []
        while current != start:
            tile_center_x = (
                current[0] * self.scaled_tile_size + self.scaled_tile_size / 2
            )
            tile_center_y = (
                current[1] * self.scaled_tile_size + self.scaled_tile_size / 2
            )
            path.append((tile_center_x, tile_center_y))
            current = came_from[current]
        path.reverse()

        smoothed_path = self._path_smoothing(path)

        return smoothed_path

    def _has_line_of_sight(self, p1, p2):
        # Convert pixel coordinates back to grid coordinates (col, row)
        x1 = int(p1[0] / self.scaled_tile_size)
        y1 = int(p1[1] / self.scaled_tile_size)
        x2 = int(p2[0] / self.scaled_tile_size)
        y2 = int(p2[1] / self.scaled_tile_size)

        # Bresenham's Line Algorithm setup
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x_sign = 1 if x1 < x2 else -1
        y_sign = 1 if y1 < y2 else -1
        error = dx - dy

        # Walk the grid from start to finish
        while x1 != x2 or y1 != y2:
            # Ensure we stay within the grid bounds
            if 0 <= y1 < len(self.grid) and 0 <= x1 < len(self.grid[0]):
                if self.grid[y1][x1] == 1:  # Hit a collision tile
                    return False
            else:
                return False  # Treat out-of-bounds as blocked

            e2 = 2 * error
            if e2 > -dy:
                error -= dy
                x1 += x_sign
            if e2 < dx:
                error += dx
                y1 += y_sign

        return True

    def _path_smoothing(self, path):
        if len(path) <= 2:
            return path

        smoothed_path = [path[0]]
        current_index = 0

        while current_index < len(path) - 1:
            furthest_visible_index = current_index + 1

            # Checking furthest path node in line of sight
            for i in range(len(path) - 1, current_index, -1):
                if self._has_line_of_sight(path[current_index], path[i]):
                    furthest_visible_index = i
                    break

            smoothed_path.append(path[furthest_visible_index])
            current_index = furthest_visible_index

        return smoothed_path
