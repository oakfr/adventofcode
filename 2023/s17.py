import sys
import math

UP = 0
RIGHT = 1
LEFT = 2
DOWN = 3

filename = sys.argv[1]

data = open(filename, 'r').readlines()

mp = [[int(x) for x in line.strip()] for line in data]

rows = len(mp)
cols = len(mp[0])

def opposite_direction(d):
    if d == UP: return DOWN
    if d == DOWN: return UP
    if d == RIGHT: return LEFT
    if d == LEFT: return RIGHT
    assert(False)
    return None

def all_neighbors(pos, rows, cols):
    r = pos[0]
    c = pos[1]
    out = [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]
    out = filter(lambda x:x[0] >= 0, out)
    out = filter(lambda x:x[1] >= 0, out)
    out = filter(lambda x:x[0] < rows, out)
    out = filter(lambda x:x[1] < cols, out)
    return list(out)

def neighbors(pos, rows, cols):
    r = pos[0]
    c = pos[1]
    d = pos[2]
    x = pos[3]
    o1 = (r-1, c, UP, x+1 if UP == d else 0)
    o2 = (r+1, c, DOWN, x+1 if DOWN == d else 0)
    o3 = (r, c-1, LEFT, x+1 if LEFT == d else 0)
    o4 = (r, c+1, RIGHT, x+1 if RIGHT == d else 0)
    out = [o1, o2, o3, o4]
    if x < 3:
        out = filter(lambda x:x[2] == d, out)
    if d:
        out = filter(lambda x:x[2] != opposite_direction(d), out) # no going backward
    out = filter(lambda x:x[3] < 11, out) # 
    #out = filter(lambda x:x[3] >= 4, out) # 
    out = filter(lambda x:x[0] >= 0, out) # stay in the grid
    out = filter(lambda x:x[1] >= 0, out)
    out = filter(lambda x:x[0] < rows, out)
    out = filter(lambda x:x[1] < cols, out)
    return list(out)

# dijkstra's
def find():
    unvisited = {}
    for c in range(cols):
        for r in range(rows):
            for d in range(4):
                for steps in range(10):
                    unvisited[(r,c,d,steps)] = math.inf # r, c, direction, count

    dist = {}
    for c in range(cols):
        for r in range(rows):
            for d in range(4):
                for steps in range(10):
                    dist[(r,c,d,steps)] = math.inf
    curr = (0,0,1,0) # r, c, direction, count
    dist[curr] = 0

    targets = {}

    while True:
        # process neighbors
        for ne in neighbors(curr, rows, cols):
            if ne in unvisited:
                dist[ne] = min(dist[ne], dist[curr] + mp[ne[0]][ne[1]])
                targets[ne] = dist[ne]
        unvisited.pop(curr)
        if curr in targets: targets.pop(curr)
        # find next curr (unvisited with smallest distance)
        if not unvisited:
            break
        v = [(a,dist[a]) for a in targets]
        if not v:
            break
        v = min(v, key=lambda a: a[1])
        if v[1] < math.inf:
            curr = v[0]
        else:
            break
    return dist

import time

start = time.time()
dist = find()
end = time.time()
print(f'elapsed time: {(end-start)*1000:.2f} ms')

out = []
for k,v in dist.items():
    if k[0] == rows-1 and k[1] == cols-1 and v != math.inf:
        out.append(v)
print(min(out))
