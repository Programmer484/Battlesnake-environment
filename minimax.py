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
