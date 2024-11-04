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


















"""user.py"""
user1_move_name = None
user2_move_name = None
def user1_move(game_state):
    return user1_move_name
def user2_move(game_state):
    return user2_move_name
