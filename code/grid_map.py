from settings import *
from queue import PriorityQueue

class GridMap:
    def __init__(self):
        self.scale = 1
        self.scaled_tile_size = TILE_SIZE / self.scale


    def construct(self, map :  pytmx.TiledMap):
        self.grid = [[0 for i in range(map.width * self.scale)] for j in range(map.height * self.scale)]
        for obj in map.get_layer_by_name('Collisions'):
            grid_width = math.ceil(obj.width / self.scaled_tile_size) 
            grid_height = math.ceil(obj.height / self.scaled_tile_size)
            for i in range(grid_height):
                for j in range(grid_width):
                    self.grid[int(obj.y / self.scaled_tile_size) + i][int(obj.x / self.scaled_tile_size) + j] = 1
        self.show_map()


    def show_map(self, filename = "map.txt", diff_grid = None):
        used_grid = None
        if diff_grid:
            used_grid = diff_grid
        else:
            used_grid = self.grid


        with open(filename, "w") as f:
            for rows in used_grid:
                for item in rows:
                    f.write('%d ' %item)
                f.write('\n')


    def show_path(self, path):
        for point in path:
            self.grid[int(point[1] / self.scaled_tile_size)][int(point[0] / self.scaled_tile_size)] = 5
        self.show_map("path.txt")
        for point in path:
            self.grid[int(point[1] / self.scaled_tile_size)][int(point[0] / self.scaled_tile_size)] = 0


    def get_path(self, start_cords , goal_cords):
        def get_neighboars(point : tuple[int, int]):
            neighbors = [(point[0] + 1 , point[1]), (point[0] - 1, point[1]), (point[0] , point[1] + 1), (point[0] , point[1] - 1)]
            valid_neigh = []
            for n in neighbors:
                #n[1] == y == row | n[0] == x == col
                if self.grid[n[1]][n[0]] == 0:
                    valid_neigh.append(n)
            if len(valid_neigh) == 0:
                print("err")
            return valid_neigh


        def heuristic(a, b):
            # Manhattan distance on a square grid
            return abs(a[0] - b[0]) + abs(a[1] - b[1]) 
        
        # x = col , y = row
        grid_start_x = int(start_cords[0] / self.scaled_tile_size)
        grid_start_y = int(start_cords[1] / self.scaled_tile_size)
        grid_goal_x = int(goal_cords[0] / self.scaled_tile_size)
        grid_goal_y = int(goal_cords[1] / self.scaled_tile_size)
        
        start = (grid_start_x, grid_start_y)
        goal = (grid_goal_x, grid_goal_y)

        p_queue = PriorityQueue()
        p_queue.put((0, start))
        came_from = dict()
        cost_so_far = dict()
        came_from[start] = None
        cost_so_far[start] = 0

        # MAP GRID
        while not p_queue.empty():
            current = p_queue.get()[1]
            if current == goal:
                break
            for next in get_neighboars(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(next, goal)
                    p_queue.put((priority, next))
                    came_from[next] = current
        
        # BUILD PATH
        current = goal
        path = []
        while current != start:
            tile_center_x = current[0] * self.scaled_tile_size + self.scaled_tile_size / 2
            tile_center_y = current[1] * self.scaled_tile_size + self.scaled_tile_size / 2
            path.append((tile_center_x, tile_center_y))
            current = came_from[current]
        path.reverse()

        return path


