import copy
import random
import sys
import time

import pygame
from pprint import pp

import user
from minimax import minimax_move
from ab_minimax import ab_minimax_move

game_state = {'game': {'id': 'a2755c48-6aaa-46f6-92b5-b08d0f9b650b',
      'ruleset': {'name': 'standard',
                  'version': 'v1.2.3',
                  'settings': {'foodSpawnChance': 15,
                               'minimumFood': 1,
                               'hazardDamagePerTurn': 0,
                               'hazardMap': '',
                               'hazardMapAuthor': '',
                               'royale': {'shrinkEveryNTurns': 0},
                               'squad': {'allowBodyCollisions': False,
                                         'sharedElimination': False,
                                         'sharedHealth': False,
                                         'sharedLength': False}}},
      'map': 'standard',
      'timeout': 500,
      'source': 'custom'},
'turn': 0,
'board': {'height': 11,
       'width': 11,
       'snakes': [{'id': 'gs_Kt8w4jv9k8gdPxyXrwJfSkjT',
                   'name': 'Ryan',
                   'latency': '',
                   'health': 100,
                   'body': [{'x': 1, 'y': 1},
                            {'x': 1, 'y': 1},
                            {'x': 1, 'y': 1}],
                   'head': {'x': 1, 'y': 1},
                   'length': 3,
                   'shout': '',
                   'squad': '',
                   'customizations': {'color': '#44ff44',
                                      'head': 'default',
                                      'tail': 'default'}},
                  {'id': 'gs_THRHmwJrPWP7pg33Hq7CRkp9',
                   'name': 'Gary',
                   'latency': '',
                   'health': 100,
                   'body': [{'x': 9, 'y': 1},
                            {'x': 9, 'y': 1},
                            {'x': 9, 'y': 1}],
                   'head': {'x': 9, 'y': 1},
                   'length': 3,
                   'shout': '',
                   'squad': '',
                   'customizations': {'color': '#ffe58f',
                                      'head': 'glasses',
                                      'tail': 'freckled'}}],
       'food': [{'x': 0, 'y': 2}, {'x': 10, 'y': 2}, {'x': 5, 'y': 5}],
       'hazards': []},
             }
def user1_input():
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_w]:
        user.user1_move_name = 'up'
    if keys_pressed[pygame.K_a]:
        user.user1_move_name = 'left'
    if keys_pressed[pygame.K_d]:
        user.user1_move_name = 'right'
    if keys_pressed[pygame.K_s]:
        user.user1_move_name = 'down'

def user2_input():
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_UP]:
        user.user2_move_name = 'up'
    if keys_pressed[pygame.K_LEFT]:
        user.user2_move_name = 'left'
    if keys_pressed[pygame.K_RIGHT]:
        user.user2_move_name = 'right'
    if keys_pressed[pygame.K_DOWN]:
        user.user2_move_name = 'down'

class Game:
    def __init__(self, game_state, controllers: list):
        self.game_state = game_state
        self.Tsize = 50
        self.controllers = controllers
    """CONTROLLER METHODS"""
    def convert_move_to_dict(self, move_name):
        move_options = [{'move_name': 'left', 'x': -1, 'y': 0}, {'move_name': 'right', 'x': 1, 'y': 0}, {'move_name': 'up', 'x': 0, 'y': 1}, {'move_name': 'down', 'x': 0, 'y': -1}]
        for move in move_options:
            if move['move_name'] == move_name:
                return move
        return None
    def get_moves(self):
        for i, controller in enumerate(self.controllers):
            game_state = copy.deepcopy(self.game_state)
            game_state['you'] = copy.deepcopy(game_state['board']['snakes'][i])
            start_time = pygame.time.get_ticks()
            move_name = controller(game_state)
            move_time = pygame.time.get_ticks() - start_time
            #print(f"{game_state['board']['snakes'][i]['name']} --> {move_time}")
            if move_time > self.game_state['game']['timeout']:
                move_name = None
                print(f"{game_state['board']['snakes'][i]['name']} --> TIMEOUT")
            if self.convert_move_to_dict(move_name) != None:
                self.game_state['board']['snakes'][i]['move'] = self.convert_move_to_dict(move_name)

    """SETUP METHODS"""
    def create_snakes(self):
        pass
    def starting_food(self):
        # Exactly 2 spaces away from snake
        # Further from the center in at least one direction
        # Not in the corner
        pass

    """IN GAME METHODS"""
    def simulate_movement(self):
        for snake in self.game_state['board']['snakes']:
            snake['body'].insert(0, {'x': snake['head']['x'] + snake['move']['x'], \
                                    'y': snake['head']['y'] + snake['move']['y']}) # TODO include snake['move'] in the game_state
            snake['head'] = snake['body'][0]
            del snake['body'][-1]
    def simulate_starvation(self):
        for snake in self.game_state['board']['snakes']:
            snake['health'] -= 1
    def simulate_hazards(self):
        # TODO hazard spawning
        for snake in self.game_state['board']['snakes']:
            for hazard in self.game_state['board']['hazards']:
                if snake['head'] == hazard:
                    snake['health'] -= self.game_state['game']['ruleset']['settings']['hazardDamagePerTurn']
    def simulate_feeding(self):
        consumed_food = []
        for snake in self.game_state['board']['snakes']:
            for food in self.game_state['board']['food']:
                if snake['head'] == food:
                    consumed_food.append(food)
                    snake['body'].append(snake['body'][-1].copy())
                    snake['health'] = 100
                    snake['length'] = len(snake['body'])
        for food in consumed_food:
            if food in self.game_state['board']['food']:
                self.game_state['board']['food'].remove(food)
    def out_of_bounds(self, snake):
        if snake['head']['x'] < 0 or snake['head']['y'] < 0 or snake['head']['x'] >= self.game_state['board']['width'] or snake['head']['y'] >= self.game_state['board']['height']:
            return True
    def body_collision(self, colliding_snake, other_snake):
        if colliding_snake['head'] in other_snake['body'][1:]:
            return True
    def lost_head_to_head(self, colliding_snake, other_snake):
        if colliding_snake['head'] == other_snake['head']:
            if colliding_snake['length'] <= other_snake['length']:
                return True
    def simulate_eliminations(self):
        eliminated_snakes = []
        collision_eliminations = []
        for snake in self.game_state['board']['snakes']:
            if snake in eliminated_snakes:
                continue
            if snake['health'] <= 0:
                eliminated_snakes.append(snake)
        for snake in self.game_state['board']['snakes']:
            if snake in eliminated_snakes:
                continue
            if self.out_of_bounds(snake):
                eliminated_snakes.append(snake)
        for snake in self.game_state['board']['snakes']:
            if snake in eliminated_snakes:
                continue
            for other in self.game_state['board']['snakes']:
                if other in eliminated_snakes:
                    continue
                if self.body_collision(snake, other):
                    collision_eliminations.append(snake)
                if snake == other:
                    continue
                if self.lost_head_to_head(snake, other):
                    collision_eliminations.append(snake)
        eliminated_snakes = eliminated_snakes + collision_eliminations
        if eliminated_snakes != []:
            for snake in eliminated_snakes:
                if snake in self.game_state['board']['snakes']:
                    self.game_state['board']['snakes'].remove(snake)
    def check_food_needing_placement(self):
        if len(self.game_state['board']['food']) < self.game_state['game']['ruleset']['settings']['minimumFood']:
            return self.game_state['game']['ruleset']['settings']['minimumFood'] - len(self.game_state['board']['food'])
        elif random.randint(1, 100) <= self.game_state['game']['ruleset']['settings']['foodSpawnChance'] and self.game_state['game']['ruleset']['settings']['foodSpawnChance'] != 0:
            return 1
        else:
            return 0
    def get_unoccupied_points(self):
        unoccupied_points = []
        for y in range(self.game_state['board']['height']):
            for x in range(self.game_state['board']['width']):
                empty = True
                if {'x': x, 'y':y} in self.game_state['board']['food']:
                    empty = False
                else:
                    for snake in self.game_state['board']['snakes']:
                        if {'x': x, 'y':y} in snake['body']:
                            empty = False
                            break
                if empty == True:
                    unoccupied_points.append({'x': x, 'y':y})
        return unoccupied_points
    def place_food_randomly(self, num_food):
        unoccupied_points = self.get_unoccupied_points()
        for i in range(num_food):
            if len(unoccupied_points) > 0:
                food = random.choice(unoccupied_points)
                self.game_state['board']['food'].append(food)
                unoccupied_points.remove(food)
            else:
                return None
    def simulate_food_spawn(self):
        num_food = self.check_food_needing_placement()
        self.place_food_randomly(num_food)
    def check_game_end(self):
        if self.game_state['game']['ruleset']['name'] == "solo" and len(self.game_state['board']['snakes']) == 0:
            return True
        elif self.game_state['game']['ruleset']['name'] != "solo" and len(self.game_state['board']['snakes']) < 2:
            return True
        else:
            return False

    """SIMULATE TURN"""
    def simulate_turn(self):
        self.simulate_movement()
        self.simulate_starvation()
        self.simulate_hazards()    
        self.simulate_feeding()
        self.simulate_food_spawn()
        self.simulate_eliminations()
        self.game_state["turn"] += 1
    """DRAW METHODS"""
    def snake_and_food_grid(self):
        grid = []
        for y in range(self.game_state['board']['height']):
            grid.append([(0,)] * self.game_state['board']['width'])
        for food in self.game_state['board']['food']:
            grid[(self.game_state['board']['height'] - 1) - food['y']][food['x']] = (1, (200, 127, 0))
        for snake in self.game_state['board']['snakes']:
            grid[(self.game_state['board']['height'] - 1) - snake['head']['y']][snake['head']['x']] = (2, snake['customizations']['color'])
            for segment in snake['body'][1:-1]:
                grid[(self.game_state['board']['height'] - 1) - segment['y']][segment['x']] = (3, snake['customizations']['color'])
            tail = snake['body'][-1]
            grid[(self.game_state['board']['height'] - 1) - tail['y']][tail['x']] = (4, snake['customizations']['color'])
        return grid
    def hazard_grid(self):
        pass
    def draw_board(self, window):
        sf_grid = self.snake_and_food_grid()
        window.fill((0, 0, 0))
        line_color = (250, 250, 250)
        square_color = (237, 237, 237)
        for y in range(self.game_state['board']['height']):
            for x in range(self.game_state['board']['width']):
                if sf_grid[y][x][0] == 0:
                    pygame.draw.rect(window, square_color, (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize))
                    pygame.draw.rect(window, line_color, (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize), 3)
                elif sf_grid[y][x][0] == 1:    
                    pygame.draw.rect(window, square_color, (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize))
                    pygame.draw.rect(window, line_color, (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize), 3)
                    pygame.draw.circle(window, sf_grid[y][x][1], (x*self.Tsize + 25, y*self.Tsize + 25), 15)
                elif sf_grid[y][x][0] == 2:
                    pygame.draw.rect(window, sf_grid[y][x][1], (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize))
                    pygame.draw.rect(window, (255, 255, 255), (x*self.Tsize + 2/5*self.Tsize, y*self.Tsize + 2/5*self.Tsize, 1/5*self.Tsize, 1/5*self.Tsize))
                    pygame.draw.rect(window, line_color, (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize), 3)
                elif sf_grid[y][x][0] == 3:
                    pygame.draw.rect(window, sf_grid[y][x][1], (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize))
                    pygame.draw.rect(window, line_color, (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize), 3)
                elif sf_grid[y][x][0] == 4:
                    pygame.draw.rect(window, sf_grid[y][x][1], (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize))
                    pygame.draw.rect(window, line_color, (x*self.Tsize, y*self.Tsize, self.Tsize, self.Tsize), 3)

        for snake in self.game_state['board']['snakes']:
            for i in range(snake['length'] - 1):
                self.fill_gaps(window, snake, i)
    def neighbour(self, segment, neighbour):
        if neighbour['x'] < segment['x']:
            return "left"
        elif neighbour['x'] > segment['x']:
            return "right"
        elif neighbour['y'] < segment['y']:
            return "down"
        elif neighbour['y'] > segment['y']:
            return "up"
    def fill_gaps(self, window, snake, i):
        if self.neighbour(snake['body'][i], snake['body'][i + 1]) == "left":
            pygame.draw.rect(window, snake['customizations']['color'], (snake['body'][i]['x'] * self.Tsize - 3, (self.game_state['board']['width'] - 1 - snake['body'][i]['y']) * self.Tsize + 3, 6, self.Tsize - 6))
        elif self.neighbour(snake['body'][i], snake['body'][i + 1]) == "right":
            pygame.draw.rect(window, snake['customizations']['color'], (snake['body'][i]['x'] * self.Tsize + self.Tsize - 3, (self.game_state['board']['width'] - 1 - snake['body'][i]['y']) * self.Tsize + 3, 6, self.Tsize - 6))
        elif self.neighbour(snake['body'][i], snake['body'][i + 1]) == "up":
            pygame.draw.rect(window, snake['customizations']['color'], (snake['body'][i]['x'] * self.Tsize + 3, (self.game_state['board']['height'] - 1 - snake['body'][i]['y']) * self.Tsize - 3, self.Tsize - 6, 6))
        elif self.neighbour(snake['body'][i], snake['body'][i + 1]) == "down":
            pygame.draw.rect(window, snake['customizations']['color'], (snake['body'][i]['x'] * self.Tsize + 3, (self.game_state['board']['height'] - 1 - snake['body'][i]['y']) * self.Tsize + self.Tsize - 3, self.Tsize - 6, 6))
    def draw_info(self, window):
        font = pygame.font.SysFont(None, 40)
        for i, snake in enumerate(self.game_state['board']['snakes']):
            name = snake['name']
            length = snake['length']
            health = snake['health']
            text = font.render(f"{name} length: {length}, hp: {health}", True, (255, 255, 255)) 
            window.blit(text, (self.Tsize * self.game_state['board']['height'] + 20, 20 + i*30))
            window.blit(text, (self.Tsize * self.game_state['board']['height'] + 20, 20 + i*30))
    """UTILITY METHODS"""
    def print_grid(self):
        grid = []
        for y in range(self.game_state['board']['height']):
            grid.append([0] * self.game_state['board']['width'])
        for food in self.game_state['board']['food']:
            grid[(self.game_state['board']['height'] - 1) - food['y']][food['x']] = 1
        for i, snake in enumerate(self.game_state['board']['snakes']):
            snake['grid_number'] = 3 * i + 2
            grid[(self.game_state['board']['height'] - 1) - snake['head']['y']][snake['head']['x']] = snake['grid_number'] + 2
            for segment in snake['body'][1:-1]:
                grid[(self.game_state['board']['height'] - 1) - segment['y']][segment['x']] = snake['grid_number'] + 1
            tail = snake['body'][-1]
            grid[(self.game_state['board']['height'] - 1) - tail['y']][tail['x']] = snake['grid_number']
        print("============================ TURN " + str(self.game_state['turn']) + " START ============================")
        for y in grid:
            print(y)
        print("============================ TURN " + str(self.game_state['turn']) + " END ============================")
controllers = [ab_minimax_move, user.user1_move]

pygame.init()
g = Game(game_state, controllers)
for snake in g.game_state['board']['snakes']:
    snake['move'] = {'move_name': 'up', 'x': 0, 'y': 1}
SCREEN_WIDTH = g.Tsize * g.game_state['board']['height'] + 400
SCREEN_HEIGHT = g.Tsize * g.game_state['board']['height']
FRAME_RATE = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.set_alpha(0)
clock = pygame.time.Clock()

last_time = 0
g.draw_board(screen)
g.draw_info(screen)
pygame.display.flip()
user_time = pygame.time.get_ticks()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if user.user1_move_name is None and  pygame.time.get_ticks() - user_time > 250:
        user1_input()
    if user.user2_move_name is None and  pygame.time.get_ticks() - user_time > 250:
        user2_input()
    current_time = pygame.time.get_ticks()
    
    if current_time - last_time > 100 and user.user1_move_name is not None:
        last_time = current_time
        if not g.check_game_end():
            g.get_moves()
            g.simulate_turn()
            g.draw_board(screen)
            g.draw_info(screen)
            g.print_grid()
            user.user1_move_name = None
            user.user2_move_name = None
            user_time = pygame.time.get_ticks()

    pygame.display.flip()
    clock.tick(FRAME_RATE)


























"""minimax.py"""
import copy
import itertools
import math
import time

#Debugging
def gprint(grid):
    for row in grid:
        print(row)
# Miscellaneous
def set_you(game_state):
    # sets the ['you'] key as a reference to snake of interest in ['board']['snakes']
    target_snake_id = game_state['you']['id']
    for snake in game_state['board']['snakes']:
        if snake['id'] == target_snake_id:
            game_state['you'] = snake    
# Simulation
def simulate_move(snake, move: dict):
    snake['body'].insert(0, {'x': snake['head']['x'] + move['x'], 'y': snake['head']['y'] + move['y']})
    snake['head'] = snake['body'][0]
    del snake['body'][-1]
def simulate_starvation(board):
    for snake in board['snakes']:
        snake['health'] -= 1
def simulate_hazards():
# hazard_damage = game_state['game']['ruleset']['settings']['hazardDamagePerTurn']
# set variables for all ruleset settings so they aren't passed into minimax func
    # for snake in board['snakes']:
    #     for hazard in ['harzards']:
    #         if snake['head'] == hazard:
    #             snake['health'] -= hazard_damage
    pass    
def simulate_feeding(board):
    consumed_food = []
    for snake in board['snakes']:
        for food in board['food']:
            if snake['head'] == food:
                consumed_food.append(food)
                snake['body'].append(snake['body'][-1].copy())
                snake['health'] = 100
                snake['length'] = len(snake['body'])
    for food in consumed_food:
        if food in board['food']:
            board['food'].remove(food)
def out_of_bounds(snake, board):
    if snake['head']['x'] < 0 or snake['head']['y'] < 0 or snake['head']['x'] >= board['width'] or snake['head']['y'] >= board['height']:
        return True
def body_collision(colliding_snake, other_snake):
    if colliding_snake['head'] in other_snake['body'][1:]:
        return True
def lost_head_to_head(colliding_snake, other_snake):
    if colliding_snake['head'] == other_snake['head']:
        if len(colliding_snake['body']) <= len(other_snake['body']):
            return True
def simulate_eliminations(board):
    eliminated_snakes = []
    collision_eliminations = []
    for snake in board['snakes']:
        if snake in eliminated_snakes:
            continue
        if snake['health'] <= 0:
            eliminated_snakes.append(snake)
    for snake in board['snakes']:
        if snake in eliminated_snakes:
            continue
        if out_of_bounds(snake, board):
            eliminated_snakes.append(snake)
    for snake in board['snakes']:
        if snake in eliminated_snakes:
            continue
        for other in board['snakes']:
            if other in eliminated_snakes:
                continue
            if body_collision(snake, other):
                collision_eliminations.append(snake)
            if snake == other:
                continue
            if lost_head_to_head(snake, other):
                collision_eliminations.append(snake)
    eliminated_snakes = eliminated_snakes + collision_eliminations
    if eliminated_snakes != []:
        for snake in eliminated_snakes:
            if snake in board['snakes']:
                board['snakes'].remove(snake)
def check_win_or_loss(board, snake, mode):
    if mode == "standard":
        if len(board['snakes']) == 0:
            return -0.5 # tie
        elif snake not in board['snakes']:
            return -1   # loss
        elif len(board['snakes']) == 1:
            return 1  # win
        else:
            return None
    elif mode == "solo":
        if len(board['snakes']) == 0:
            return -1
        else:
            return None
# Math
def sigmoid(x):
    return 1/(1 + math.e**-x)
def calc_distance(x1, x2, y1, y2):
    return abs(x1 - x2) + abs(y1 - y2)
# Pattern recognition
def rotated(grid, num_rotations):
    rotated = copy.deepcopy(grid)
    for x in range(num_rotations):
        rotated = list(map(list, zip(*rotated[::-1])))
    return rotated
def horizontally_flipped(grid):
    flipped_grid = copy.deepcopy(grid)
    for row in flipped_grid:
        row.reverse()
    return flipped_grid
def vertically_flipped(grid):
    flipped_grid = copy.deepcopy(grid)
    flipped_grid.reverse()
    return flipped_grid
def all_transformations(grid):
    transformations = []
    for i in range(4):
        rotated_grid = rotated(grid, i)
        if rotated_grid not in transformations:
            transformations.append(rotated_grid)
        h_flipped_grid = horizontally_flipped(rotated_grid)
        if h_flipped_grid not in transformations:
            transformations.append(h_flipped_grid)
        v_flipped_grid = vertically_flipped(rotated_grid)
        if v_flipped_grid not in transformations:
            transformations.append(v_flipped_grid)
    return transformations
def expand_grid(grid, padding):
    expanded_grid = copy.deepcopy(grid)
    for row in expanded_grid:
        for p in range(padding):
            row.insert(0, 2)
            row.append(2)
    for p in range(padding):
        expanded_grid.insert(0, [2] * len(row))
        expanded_grid.append([2] * len(row))
    return expanded_grid
def create_head_area_grid(snake, board_grid, y_range, x_range):
    # grid of area around head
    head_area_grid = []
    padding = max(y_range, x_range)
    y = len(board_grid) - snake['head']['y'] - 1
    x = snake['head']['x']
    board_grid = expand_grid(board_grid, padding)
    for row in board_grid[(y - y_range + padding): (y + y_range + 1 + padding)]:
        new_row = row[(x - x_range + padding) : (x + x_range + 1 + padding)]
        head_area_grid.append(new_row)
    return head_area_grid
def match_grid(grid_criteria, grid):
    grid_match = True
    for y in range(len(grid_criteria)):
        for x in range(len(grid_criteria[0])):
            if grid_criteria[y][x] == 5 or grid_criteria[y][x] == grid[y][x]:
                continue
            else:
                grid_match = False
                return grid_match
    return grid_match
def edge_cutoff(snake, board_grid):
    start_pattern1 = [[2, 5, 3],
                     [2, 3, 2],
                     [2, 2, 5]]
    start_pattern2 = [[2, 5, 5],
                     [2, 3, 5],
                     [2, 2, 4]]
    patterns = [start_pattern1, start_pattern2]
    for start_pattern in patterns:
        grid_criteria_list = all_transformations(start_pattern)
        y_range = int((len(start_pattern) - 1)/2)
        x_range = int((len(start_pattern[0]) - 1)/2)
        head_area_grid = create_head_area_grid(snake, board_grid, y_range, x_range)
        for grid_criteria in grid_criteria_list:
            if match_grid(grid_criteria, head_area_grid):
                return True
    return False
# Flood fill
def create_grid(board, you):
    grid = []
    for y in range(board['height']):
        grid.append([0] * board['width'])
    snakes = board['snakes']
    for snake in snakes:
        if snake['length'] > you['length']:
            grid[(board['height'] - 1) - snake['head']['y']][snake['head']['x']] = 4
        else:
            grid[(board['height'] - 1) - snake['head']['y']][snake['head']['x']] = 3
        for segment in snake['body'][1:-1]:
            grid[(board['height'] - 1) - segment['y']][segment['x']] = 2
        tail = snake['body'][-1]
        grid[(board['height'] - 1) - tail['y']][tail['x']] = 1
    return grid
def flood_fill(grid, x, y, width, height, required_space):
    grid = copy.deepcopy(grid)
    queue = []
    queue.append((x - 1, y))
    queue.append((x + 1, y))
    queue.append((x, y + 1))
    queue.append((x, y - 1))
    space = 0
    while queue != []:
        x, y = queue[0]
        if y < 0 or y >= height or x < 0 or x >= width or grid[(height - 1) - y][x] in {2, 3, 4}:
            queue.remove((x, y))
            continue
        elif grid[(height - 1) - y][x] == 1:
            space = required_space
            return space
        else:
            grid[(height - 1) - y][x] = 2
            space += 1
            if space == required_space:
                return space
        queue.append((x - 1, y))
        queue.append((x + 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))
    return space
def flood_fill_eval(space, body_length):
    space_to_body_ratio = space/body_length
    return space_to_body_ratio - 1
# Food
def nearest_food_dist(board, snake):
    nearest_food_distance = 100
    if len(board['food']) > 0:
        for food in board['food']:
            distance = calc_distance(snake['head']['x'],food['x'], snake['head']['y'], food['y'])
            if distance < nearest_food_distance:
                nearest_food_distance = distance
        return nearest_food_distance
    else:
        return 10
def food_eval(food_distance):
    if food_distance <= 16:
        return (-food_distance/16 + 1)/11
    else:
        return 0
# Center heuristic
def center_eval(distance):
    return (-distance/16 + 1)/12



def minimax_move(game_state):
    '''SIMULATOR'''
    # possible game_states
    move_names = ['left', 'right', 'up', 'down']
    move_options = [{'move_name': 'left', 'x': -1, 'y': 0}, {'move_name': 'right', 'x': 1, 'y': 0}, {'move_name': 'up', 'x': 0, 'y': 1}, {'move_name': 'down', 'x': 0, 'y': -1}]
    move_options_by_player = []
    
    for snake in game_state['board']['snakes']:
        move_options_by_player.append(move_options)
    move_permutations = list(itertools.product(*move_options_by_player))
    current_game_node = {'game_state': game_state}
    set_you(current_game_node['game_state'])
    leaf_nodes = [current_game_node]
    # simulator output
    game_tree = []
    # simulator settings
    depth = 2

    
    '''CREATE GAME TREE'''
    for i in range(depth):
        nodes_to_expand = leaf_nodes
        leaf_nodes = []
        node_level = []
        for parent_node in nodes_to_expand:
            # group leaf nodes based on the parent state and move of 'you' snake for before adding to node_level
            node_group = {'left':[], 'right':[], 'up':[], 'down':[]}
            node_group['parent'] = parent_node
            for move_set in move_permutations:
                child_node = {}
                child_node['game_state'] = copy.deepcopy(parent_node['game_state'])
                for i in range(len(child_node['game_state']['board']['snakes'])):
                    # group child nodes by move of 'you' snake
                    if child_node['game_state']['board']['snakes'][i]['id'] == child_node['game_state']['you']['id']:
                        node_group[move_set[i]['move_name']].append(child_node)
                        child_node['target_move'] = move_set[i]['move_name']
                    simulate_move(child_node['game_state']['board']['snakes'][i], move_set[i])
                simulate_starvation(child_node['game_state']['board'])
                simulate_feeding(child_node['game_state']['board'])
                simulate_eliminations(child_node['game_state']['board'])
                child_node['game_state']['turn'] += 1
                if len(child_node['game_state']['you']['body']) > len(parent_node['game_state']['you']['body']) or 'ate' in parent_node.keys():
                    child_node['ate'] = True
                game_end_value = check_win_or_loss(child_node['game_state']['board'], child_node['game_state']['you'], 'standard')
                if game_end_value != None:
                    child_node['value'] = game_end_value
                else:
                    leaf_nodes.append(child_node)
                child_node['grid'] = create_grid(child_node['game_state']['board'], child_node['game_state']['you'])
            node_level.append(node_group)
        game_tree.append(node_level)
    

    '''EVALUATE LEAF NODES'''
    for game_node in leaf_nodes:
        # Flood fill
        grid = create_grid(game_node['game_state']['board'], game_node['game_state']['you'])
        if edge_cutoff(game_node['game_state']['you'], grid):
            flood_fill_evaluation = -0.8
        else:
            space = flood_fill(grid, game_node['game_state']['you']['head']['x'], game_node['game_state']['you']['head']['y'], \
                                game_node['game_state']['board']['width'], game_node['game_state']['board']['height'], len(game_node['game_state']['you']['body']))
            flood_fill_evaluation = flood_fill_eval(space, len(game_node['game_state']['you']['body']))
        best_opp_flood_fill_evaluation = 0
        for snake in game_node['game_state']['board']['snakes']:
            if snake != game_node['game_state']['you']:
                grid = create_grid(game_node['game_state']['board'], snake)
                if edge_cutoff(snake, grid):
                    opp_flood_fill_evaluation = 0.8
                    gprint(grid)
                else:
                    opp_space = flood_fill(grid, snake['head']['x'], \
                                                snake['head']['y'], \
                                                game_node['game_state']['board']['width'], \
                                                game_node['game_state']['board']['height'], \
                                                len(snake['body']))
                    opp_flood_fill_evaluation = -(flood_fill_eval(opp_space, len(snake['body'])))
                if opp_flood_fill_evaluation > 0.3 and opp_flood_fill_evaluation > best_opp_flood_fill_evaluation:
                    best_opp_flood_fill_evaluation = opp_flood_fill_evaluation

        # Food
        if 'ate' in game_node.keys():
            food_evaluation = 0.1
        else:
            food_evaluation = food_eval(nearest_food_dist(game_node['game_state']['board'], game_node['game_state']['you']))/2
        center_evaluation = center_eval(calc_distance(game_node['game_state']['you']['head']['x'], (game_node['game_state']['board']['width'] - 1)/2, game_node['game_state']['you']['head']['y'], (game_node['game_state']['board']['height'] - 1)/2))/2
        # Final
        game_node['value'] = flood_fill_evaluation + food_evaluation + best_opp_flood_fill_evaluation + center_evaluation
        
    '''PROPAGATE EVALUATION'''
    for level in range(len(game_tree) - 1, -1, -1):
        for node_group in game_tree[level]:
            target_move_vals = []
            for move_name in move_names:
                # Accounts for simultaneous nature of the game
                # Increases the minimum when not all opponent moves result in an eval of -1
                node_vals = []
                for node in node_group[move_name]:
                    node_vals.append(node['value'])
                worst_val_node = min(node_group[move_name], key = lambda node: node['value'])
                if max(node_vals) > -0.5 and min(node_vals) == -1:
                    worst_val_node['value'] = -(0.95**(level+1))
                target_move_vals.append(worst_val_node)
            best_node = max(target_move_vals, key = lambda node: node['value'])
            if level > 0:
                node_group['parent']['value'] = best_node['value']
            else:
                best_move = best_node['target_move']
    return best_move










"""user.py"""
user1_move_name = None
user2_move_name = None
def user1_move(game_state):
    return user1_move_name
def user2_move(game_state):
    return user2_move_name
