import random
from queue import PriorityQueue
from helpers.constant import DIRECTIONS
import math

region_range = {16: (5, 7), 32: (7, 10), 64: (10, 13), 72: (13, 16), 80: (13, 16)}
num_of_prisons = {16: 4, 32: 6, 64: 8, 72: 9, 80: 10}

def generate_nbs(grid):
    neighbor = set()
    for direct in DIRECTIONS:
        x, y = grid[0] + direct[0], grid[1] + direct[1]
        if x in range(1, W-1) and  y in range(1, H-1) and map[x][y] == 0:
            neighbor.add((x,y))

    return neighbor

def region_generation(grid, num_tiles, id, grids_of_region):
    map[grid[0]][grid[1]] = id
    nbs = set()

    nbs.update(generate_nbs(grid))

    while len(grids_of_region[id]) < num_tiles:
        if not len(nbs): break
        chosen = random.choice(list(nbs))
        map[chosen[0]][chosen[1]] = id
        grids_of_region[id].append(chosen)
        nbs.remove(chosen)
        nbs.update(generate_nbs(chosen))
    
    nbs_list = list(nbs)
    for chosen in nbs_list:
        appear = []
        for direct in DIRECTIONS:
            row = chosen[0] + direct[0]
            col = chosen[1] + direct[1]
            if map[row][col] != 0:
                appear.append(map[row][col])
        if len(appear) >= 3:
            s = set(appear)
            random_r = random.choice(list(s))
            map[chosen[0]][chosen[1]] = random_r
            grids_of_region[random_r].append(chosen)
            nbs_list.extend(list(generate_nbs(chosen)))

    
    return nbs_list

def treasure_generate(grids_of_region):
    pos = random.choice(grids_of_region)
    i, j = pos
    while not isinstance(map[i][j], int):
        pos = random.choice(grids_of_region)
        i, j = pos
    map[i][j] = str(map[i][j]) + ' T'
    return [i, j]


def map_generation():
    total_girds = W * H
    r_range = region_range[W]
    R = random.randint(r_range[0], r_range[1])
    sea = int(random.uniform(0.2, 0.25) * total_girds)

    region = []
    grids_of_region = [[] for i in range(R)]
    pq = PriorityQueue()
    region.append(sea)

    for r in range(R - 1, 1, -1):
        tilesLeft = total_girds - sum(region)
        avg = round(tilesLeft / r)
        tiles = random.randint(round(avg - avg / 2), round(avg + avg / 2))
        region.append(tiles)

    region.append(total_girds - sum(region))

    row = random.randint(1, W - 2)
    col = random.randint(1, H - 2)
    pq.put((0, (row, col)))

    for id in range(1, len(region)):
        grid = list(pq.get())[1]
        while map[grid[0]][grid[1]] != 0:
            grid = list(pq.get())[1]

        nbs = region_generation(grid, region[id], id, grids_of_region)

        center = (W/2, H/2)
        for nb in nbs:
            distance = abs(nb[0]-center[0])+abs(nb[1]-center[1])
            pq.put((distance, nb))

    # Treasure location
    random_region_for_treasure = random.randint(1, R-1)
    Tx, Ty = random.choice(grids_of_region[random_region_for_treasure])
    grids_of_region[random_region_for_treasure].remove((Tx, Ty))

    # Generate Prisons
    prison_num = num_of_prisons[W]
    chosen_regions = random.sample(list(range(1, R)), k = prison_num)
    chosen_prisons = []
    for id in chosen_regions:
        rand_prison = random.choice(grids_of_region[id])
        grids_of_region[id].remove(rand_prison)
        chosen_prisons.append(rand_prison)
        map[rand_prison[0]][rand_prison[1]] = f'{id}P'

    # Generate Mountains
    for id in range(1, len(grids_of_region)):
        chance = random.uniform(0, 1)
        if chance > 0.45:
            continue
        number_mountains = int(random.uniform(0.05, 0.1) * len(grids_of_region[id]))
        lst_grids = random.sample(grids_of_region[id], k=number_mountains)
        for grid in lst_grids:
            map[grid[0]][grid[1]] = f'{id}M'

    return [R, Tx, Ty]

##########
W = H = 80

filename = 'MAP/MAP32.txt'
map = [[0 for i in range(W)] for j in range(H)]
r = int(math.sqrt(W))
f = int(r * (3/2))
R, x, y = map_generation()

def format_s(s, slot, col):
    tmp = ''
    for i in range(slot - len(s)):
        tmp += ' '
    tmp += s
    if col != W-1:
        tmp += ';'
    return tmp

with open(filename, 'w') as file: 
    file.write(str(W) + ' ' + str(H) + '\n')
    file.write(str(r) + '\n')
    file.write(str(f) + '\n')
    file.write(str(R) + '\n')
    file.write(str(x) + ' ' +str(y) + '\n')

    slot = 2
    if R > 10:
        slot = 3
    for row in range(H): 
        for col in range(W):
            s = str(map[row][col])
            if col == 0:
                file.write(f'{map[row][col]};') 
            else:
                file.write(format_s(s, slot, col))
        file.write('\n')