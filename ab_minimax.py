import copy
import itertools
from pprint import pp


def convert_grid(grid):
    for row in grid:
        for num in row:
            num = [num]
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
            return 20 # tief
        elif snake not in board['snakes']:
            return -10000   # loss
        elif len(board['snakes']) == 1:
            return 10000  # win
        else:
            return None
    elif mode == "solo":
        if len(board['snakes']) == 0:
            return -1
        else:
            return None
# Evaluation
def length_eval(snake):
    return snake['length']
def calc_distance(x1, x2, y1, y2):
    return abs(x1 - x2) + abs(y1 - y2)
def nearest_food_dist(board, snake):
    nearest_food_distance = 100
    if len(board['food']) > 0:
        for food in board['food']:
            distance = calc_distance(snake['head']['x'],food['x'], snake['head']['y'], food['y'])
            if distance < nearest_food_distance:
                nearest_food_distance = distance
        return nearest_food_distance
    else:
        return 0
def food_dist_eval(board, snake):
    distance = nearest_food_dist(board, snake)
    return -distance
def create_simultaneous_fill_grid(board):
    grid = []
    for y in range(board['height']):
        row = []
        for x in range(board['width']):
            row.append([0])
        grid.append(row)
    snakes = board['snakes']
    for snake in snakes:
        grid[(board['height'] - 1) - snake['head']['y']][snake['head']['x']] = [1]
        for segment in snake['body'][1:-1]:
            grid[(board['height'] - 1) - segment['y']][segment['x']] = [2]
        tail = snake['body'][-1]
        grid[(board['height'] - 1) - tail['y']][tail['x']] = [snake['length']]
    return grid
def simultaneous_flood_fill_eval(grid, snakes, max_steps):
    height = len(grid)
    width = len(grid[0])
    grid = copy.deepcopy(grid)
    snake_list = []
    step = 0
    for snake in snakes:
        x, y = snake['head']['x'], snake['head']['y']
        snake_queue = [(x - 1, y), \
                       (x + 1, y), \
                       (x, y + 1), \
                       (x, y - 1)]
        snake_info = {'space': 0, 
                      'queue': snake_queue, 
                      'next_queue': [], 
                      'length': snake['length'],
                      'id': snake['id'],
                     }
        snake_list.append(snake_info)
    snake_list.sort(key=lambda s: s['length'], reverse=True)
    filled = False
    while not filled and step <= max_steps:
        for snake in snake_list:
            for x, y in snake['queue']:
                point_info = (snake['id'], snake['length'], step)
                if  x < 0 or x >= width or y < 0 or y >= height:
                    continue
                elif len(grid[(height - 1) - y][x]) == 1:
                    if grid[(height - 1) - y][x][0] == 0:
                        snake['space'] += 1
                        grid[(height - 1) - y][x].extend(point_info)
                        snake['next_queue'].append((x - 1, y))
                        snake['next_queue'].append((x + 1, y))
                        snake['next_queue'].append((x, y + 1))
                        snake['next_queue'].append((x, y - 1))
                    elif grid[(height - 1) - y][x][0] >= 3:
                        snake['space'] += grid[(height - 1) - y][x][0]
                        grid[(height - 1) - y][x].extend(point_info)
                        snake['next_queue'].append((x - 1, y))
                        snake['next_queue'].append((x + 1, y))
                        snake['next_queue'].append((x, y + 1))
                        snake['next_queue'].append((x, y - 1))
                elif grid[(height - 1) - y][x][1] != snake['id'] \
                and grid[(height - 1) - y][x][2] == snake['length'] \
                and grid[(height - 1) - y][x][3] == step:
                    if grid[(height - 1) - y][x][0] == 0:
                        snake['space'] += 1
                    elif grid[(height - 1) - y][x][0] >= 3:
                        snake['space'] += grid[(height - 1) - y][x][0]
            snake['queue'] = snake['next_queue']
            snake['next_queue'] = []

        filled = True
        for snake in snake_list:
            if snake['queue'] != []:
                filled = False
                break
        step += 1
    return {snake['id']: snake['space'] for snake in snake_list}
move_options = [
    {'move_name': 'left', 'x': -1, 'y': 0},
    {'move_name': 'right', 'x': 1, 'y': 0}, 
    {'move_name': 'up', 'x': 0, 'y': 1}, 
    {'move_name': 'down', 'x': 0, 'y': -1}]

def evaluate(game_state):
        grid = create_simultaneous_fill_grid(game_state['board'])
        area_control = simultaneous_flood_fill_eval(grid, game_state['board']['snakes'], 20)
        area_control_eval = area_control[game_state['you']['id']]
        opp_area_control_eval = 0
        for key in area_control:
            if key != game_state['you']['id']:
                opp_area_control_eval += area_control[key]

        grid = create_grid(game_state['board'],game_state['you'])
        evaluation = area_control_eval - opp_area_control_eval + length_eval(game_state['you']) * 10

        print("area")
        print(area_control_eval - opp_area_control_eval)
        print("length")
        print(length_eval(game_state['you']))
        return evaluation

def ab_minimax_eval(game_state, depth, alpha, beta, maximizing):
    set_you(game_state)
    game_end_eval = check_win_or_loss(game_state['board'], game_state['you'], 'standard')
    if game_end_eval is not None:
        return game_end_eval
    if depth == 0:
        return evaluate(game_state)

    if maximizing == 1:
        max_eval = -100000
        for move in move_options:
            game_state_copy = copy.deepcopy(game_state)
            simulate_move(game_state_copy['you'], move)
            # eval
            evaluation = ab_minimax_eval(game_state_copy, depth - 1, alpha, beta, -maximizing)
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval    
    else:
        min_eval = 100000
        move_options_by_player = []
        for i in range(len(game_state['board']['snakes']) - 1):
            move_options_by_player.append(move_options)
        opp_move_perms = list(itertools.product(*move_options_by_player))
        for move_set in opp_move_perms:
            # create next game_state
            game_state_copy = copy.deepcopy(game_state)
            opp_snakes = copy.copy(game_state_copy['board']['snakes'])
            opp_snakes.remove(game_state['you'])
            for i, opp in enumerate(opp_snakes):
                simulate_move(opp, move_set[i])
            simulate_starvation(game_state_copy['board'])
            simulate_feeding(game_state_copy['board'])
            simulate_eliminations(game_state_copy['board'])
            game_state_copy['turn'] += 1
            # eval
            evaluation = ab_minimax_eval(game_state_copy, depth - 1, alpha, beta, -maximizing)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval

def ab_minimax_move(game_state):
    max_eval = -100000
    for move in move_options:
        game_state_copy = copy.deepcopy(game_state)
        set_you(game_state_copy)
        simulate_move(game_state_copy['you'], move)
        evaluation = ab_minimax_eval(game_state_copy, 3, -100000, 100000, -1)
        if evaluation > max_eval:
            max_eval = evaluation
            best_move = move['move_name']
    return best_move
