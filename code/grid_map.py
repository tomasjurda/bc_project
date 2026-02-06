from settings import *
from datetime import datetime

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
        #self.show_map()


    def show_map(self, filename = "map.txt"):
        with open(filename, "w") as f:
            for rows in self.grid:
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
                
        # x = col , y = row
        grid_start_x = int(start_cords[0] / self.scaled_tile_size)
        grid_start_y = int(start_cords[1] / self.scaled_tile_size)
        grid_goal_x = int(goal_cords[0] / self.scaled_tile_size)
        grid_goal_y = int(goal_cords[1] / self.scaled_tile_size)
        start = (grid_start_x, grid_start_y)
        goal = (grid_goal_x, grid_goal_y)

        #self.grid[grid_start_y][grid_start_x] = 8
        #self.grid[grid_goal_y][grid_goal_x] = 9
        #self.show_map("pos.txt")
        #self.grid[grid_start_y][grid_start_x] = 0
        #self.grid[grid_goal_y][grid_goal_x] = 0

        queue = []
        queue.append(start)
        came_from = dict()
        came_from[start] = None

        # MAP GRID
        while len(queue) != 0:
            current = queue.pop(0)
            if current == goal:
                break
            for next in get_neighboars(current):
                if next not in came_from:
                    queue.append(next)
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


