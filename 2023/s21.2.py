import sys
from PIL import Image
import numpy as np
import random
import copy
import math

def map_to_jpg(mp, filename, scale=1.0):
    rows, cols = len(mp), len(mp[0])
    arr = np.zeros((rows, cols), dtype=np.int32)
    im = Image.fromarray(arr).convert('RGB')
    pixels = im.load()
    for r,line in enumerate(mp):
        for c,u in enumerate(line):
            if u == 1:
                pixels[r,c] = (255,255,255)
            if u == 2:
                pixels[r,c] = (255,0,0)
    im = im.resize((int(cols*scale), int(rows*scale)), Image.Resampling.LANCZOS)
    im.save(filename)


# compute number of reachable spots for a given number of steps
for steps in [65]:

    filename = sys.argv[1]

    data = [a.strip() for a in open(filename, 'r').readlines()]

    rows = len(data)
    cols = len(data[0])

    # 0 = garden, 1 = rock, 2 = accessible
    mp = [[0 for _ in range(cols)] for _ in range(rows)]

    pos = None
    for r in range(rows):
        for c in range(cols):
            mp[r][c] = 1 if data[r][c] == '#' else 0
            # mp[r][c] = 1 if random.random() < 0.12172950294271896 else 0
            if data[r][c] == 'S':
                pos = [r,c]

    # replicate the map
    factor = 3
    rowsx = factor * rows
    colsx = factor * cols
    mpx = [[0 for _ in range(colsx)] for _ in range(rowsx)]
    for r in range(rows):
        for c in range(cols):
            if mp[r][c] == 1:
                for u in range(factor):
                    for v in range(factor):
                        mpx[u*rows + r][v*cols + c] = 1

    mp = copy.deepcopy(mpx)
    rows = rowsx
    cols = colsx
    pos = [int(rowsx/2), int(colsx/2)]

    mp[pos[0]][pos[1]] = 2

    def neighbors (mp, rows, cols, r, c):
        ans = [(r-1,c), (r+1, c), (r, c-1), (r, c+1)]
        ans = filter(lambda u: u[0] >= 0 and u[1] >= 0 and u[0] < rows and u[1] < cols, ans)
        ans = filter(lambda u: mp[u[0]][u[1]] == 0, ans)
        return list(ans)

    for _ in range(steps):
        ans = []
        rem = []
        for r in range(rows):
            for c in range(cols):
                if mp[r][c] == 2:
                    ans += neighbors(mp, rows, cols, r, c)
                    rem.append((r,c))
        for u in rem:
            mp[u[0]][u[1]] = 0
        for u in ans:
            mp[u[0]][u[1]] = 2

    ans = 0
    for r in range(rows):
        for c in range(cols):
            if mp[r][c] == 2:
                ans += 1

    print(steps, ans, rows, cols)

    map_to_jpg (mp, f'png/map-21-{steps}.png', scale=1)

# fine-tuning the final solution accounting for offset
n = 404601
q = n**2
x1 = round(q/2)
x2 = x1 + 1
z = x2 * 3797 + x1 * 3716
x3 = math.ceil(n/2)
eps = (x3 * (x3 + 1) / 2 - 1 ) * 80 
ans = z + eps
print(f'{n=},{x1=}, {x2=}, {x3=}, {z=}, {eps=}, {ans=}')
