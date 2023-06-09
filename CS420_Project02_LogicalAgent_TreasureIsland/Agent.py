import random
from copy import deepcopy
from astar import astar
from collections import Counter

DIRECTIONS = {(-1, 0): 'North', (1, 0): 'South', (0, 1): 'East', (0, -1): 'West'}

class Agent:
    def __init__(self, map, pirate):
        self.map = map
        self.current_loc = self.generate_initial_loc()
        self.current_path = None
        self.found_treasure = False
        self.pirate = pirate

        # percept
        self.hint_list = []
        self.track_pirate_directs = []

        # constant
        self.size_small_scan = 3
        self.size_large_scan = 5
        self.small_step = 2
        self.large_step = 4

        # Befor ereveal
        self.potential_locs = set(self.map.prisons)
        self.potential_loc = None
        self.compare_loc = None
        self.is_used_teleport = False
    
    def run(self, cur_turn):
        message = ''
        if cur_turn == self.pirate.turn_reveal:
            self.potential_locs.difference_update(set(self.map.prisons))

        if cur_turn < self.pirate.turn_reveal:
            message += '\n' + self.agent_strategy(self.current_loc, self.current_loc, cur_turn)
        elif cur_turn < self.pirate.turn_escape:
            message += '\n' + self.agent_strategy(self.pirate.initial_loc, self.pirate.initial_loc, cur_turn)
        else:
            message += '\n' + self.agent_strategy(self.pirate.current_loc, self.pirate.current_loc, cur_turn)

        if self.found_treasure:
            message += '\n' + 'Agent found the treasure, Agent won!'
        return message

    def draw(self, win):
        AGENT = (214, 16, 16) # AGENT
        x = (self.current_loc[1] + 3/2) * self.map.grid_w
        y = (self.current_loc[0] + 3/2)* self.map.grid_h
        text = self.map.FONT.render('A', True, AGENT)
        center_rect = (x - text.get_rect().width/2, y - text.get_rect().height/2)
        win.blit(text, center_rect)

    def generate_initial_loc(self):
        init_loc = (random.randrange(0, self.map.H), random.randrange(0, self.map.W))
        while self.map.map[init_loc[0]][init_loc[1]].is_barrier() or self.map.map[init_loc[0]][init_loc[1]].entity == 'P':
            init_loc = (random.randrange(0, self.map.H), random.randrange(0, self.map.W))
        return init_loc

    def add_to_hintlist(self, hint):
        self.hint_list.append(hint)
        return f'Add {hint.name} to hint list'
    
    def is_valid(self, loc):
        row , col = loc
        if row in range(self.map.H) and col in range(self.map.W):
            return True
        return False
    
    # Basic action
    def move(self, step, direct): # direct is tuple
        self.current_loc = (self.current_loc[0] + step*direct[0], self.current_loc[1] + step*direct[1])
    
    def scan(self, size):
        top = self.current_loc[0] - (size // 2)
        left = self.current_loc[1] - (size // 2)
        for row in range(top, top + size):
            for col in range(left, left + size):
                if self.is_valid((row, col)):
                    self.map.map[row][col].make_masked()
                    if self.map.map[row][col].entity == 'T':
                        self.found_treasure = True

    # 4 ACTIONS

    def verify_hint(self): #verify hint
        rand_index = random.randint(0, len(self.hint_list)-1)
        hint = self.hint_list.pop(rand_index)
        message = f'The agent verified the {hint.name}, {hint.name} is {hint.is_verified()}'
        return message
        
    def small_move_scan(self, step, direct): # small step + small scan
        self.move(step,direct)
        self.scan(self.size_small_scan)
        message = f'Agent move {step} step to the {DIRECTIONS[direct]} and do a small scan'
        return message
    
    def large_move(self, step, direct): # Move large step
        self.move(step,direct)
        message = f'Agent move {step} step to the {DIRECTIONS[direct]}'
        return message
    
    def large_scan(self): # small step + small scan
        self.scan(self.size_large_scan)
        message = f'Agent do a large scan'
        return message

    def teleport(self, tele_loc):
        self.current_loc = deepcopy(tele_loc)
        return f'Agent teleport to the {tele_loc}'
    
    # Brain of Agent
    def is_a_potential_loc(self, prison):
            top, left = prison
            for row in range(top-2, top+2): 
                for col in range(left-2, left+2):
                    if self.is_valid((row, col)) and self.map.map[row][col].is_masked == False:
                        return True
            return False
    
    def find_step_direct(self, cur, dest):
            x = dest[0] - cur[0]
            y = dest[1] - cur[1]
            step = None
            if x:
                step = abs(x)
                x //= abs(x)
            elif y:
                step = abs(y)
                y //= abs(y)
            return (step, (x, y))
    
    def basic_strategy(self, generate_target, update_percept_target):
        message = ''
        is_used_hint = False
        if len(self.current_path) > 1:
            message += '\n' + self.verify_hint()
            is_used_hint = True
            self.update_percept(generate_target, update_percept_target)

        if len(self.current_path):
            dest = self.current_path.pop()
            step, direct = self.find_step_direct(self.current_loc, dest)

            if step in [1,2]:
                message += '\n' + self.small_move_scan(step, direct)
            elif step in [3,4]:
                message += '\n' + self.large_move(step, direct)

        if len(self.current_path) == 0 and not is_used_hint:
            message += '\n' + self.large_scan()

        return message
    
    def generate_potential_locs(self, loc, steps):
        # Generate
        locs = set()
        R = self.map.H
        for step in steps:
            for row in range(0, R, step):
                for col in range(0, R, step):
                    new_loc = (row, col)
                    if self.is_valid(new_loc) and not self.map.map[new_loc[0]][new_loc[1]].is_barrier() and not self.map.map[new_loc[0]][new_loc[1]].is_masked and self.is_a_potential_loc(new_loc):
                        locs.add(new_loc)

        self.potential_locs.update(locs)

        # Checking direct
        pirate_direct = self.pirate.get_current_direct()
        if pirate_direct:
            removed_lst = set()
            self.track_pirate_directs.append(pirate_direct)
            directs = list(Counter(self.track_pirate_directs).keys())
            fre = list(Counter(self.track_pirate_directs).values())
            max_fre = max(fre)
            direct_with_max_fre = []
            for i in range(len(fre)):
                if fre[i] == max_fre:
                    direct_with_max_fre.append(directs[i])
                    break

            # Remove the one not in direct
            for loc in self.potential_locs:
                for accepted_direct in direct_with_max_fre:
                    if not self.test(self.pirate.current_loc, loc, accepted_direct):
                        removed_lst.add(loc)
            self.potential_locs.difference_update(removed_lst)


    def update_percept(self, generate_target, compare_loc):        
        self.compare_loc = compare_loc
        removed_lst = set()
        for potential_loc in self.potential_locs:
            if not self.is_a_potential_loc(potential_loc):
                removed_lst.add(potential_loc)
        
        # Current potential without checking direct
        self.potential_locs.difference_update(removed_lst)

        if not len(self.potential_locs):
            self.generate_potential_locs(generate_target, [2])
        
        if not len(self.potential_locs):
            self.generate_potential_locs(generate_target, [1])
        
        potential_score = {}
        for potential_loc in self.potential_locs:
            potential_score[potential_loc] = abs(compare_loc[0] - potential_loc[0]) + abs(compare_loc[1] - potential_loc[1])
        
        potential_score = dict(sorted(potential_score.items(), key=lambda item: item[1]))
         
        self.potential_loc = next(iter(potential_score))

        self.current_path = astar(self.current_loc, self.potential_loc, self.map, [1,2,3,4])

    
    def agent_strategy(self, generate_target, update_percept_target, cur_turn):
        message = ''
        self.update_percept(generate_target, update_percept_target)
        total_turn = len(self.current_path)
        turn_remain = None
        if cur_turn < self.pirate.turn_reveal:
            turn_remain = 999999
        elif cur_turn < self.pirate.turn_escape:
            turn_remain = self.pirate.turn_escape - cur_turn
        else:
            turn_remain = len(astar(update_percept_target, self.potential_loc, self.map, [1, 2]))
        
        # Close enough:
        if total_turn < turn_remain:
            message += '\n' + self.basic_strategy(generate_target, update_percept_target)
        # Far enough
        elif (total_turn // 2) + 1 < turn_remain:
            for i in range(2):
                if len(self.current_path):
                    dest = self.current_path.pop()
                    step, direct = self.find_step_direct(self.current_loc, dest)
                    if step in [1,2]:
                        message += '\n' + self.small_move_scan(step, direct)
                    elif step in [3,4]:
                        message += '\n' + self.large_move(step, direct)
                else:
                    message += '\n' + self.large_scan()
        # Too far
        else:
            if not self.is_used_teleport:
                message += '\n' + self.teleport(self.potential_loc)
                self.update_percept(generate_target, update_percept_target)
                self.is_used_teleport = True
                message += '\n' + self.basic_strategy(generate_target, update_percept_target)
                message += '\n' + self.verify_hint()
            else:
                message += '\n' + self.basic_strategy(generate_target, update_percept_target)
        
        return message
    
    
    def test(self, pirate_current_loc, loc, accepted_direct):
        if accepted_direct == 'East':
            if loc[1] < pirate_current_loc[1]:
                return False
        elif accepted_direct == 'West':
            if loc[1] > pirate_current_loc[1]:
                return False
        elif accepted_direct == 'North':
            if loc[0] > pirate_current_loc[0]:
                return False
        elif accepted_direct == 'South':
            if loc[0] < pirate_current_loc[0]:
                return False
        return True