import numpy as np

size = 10

grid = np.zeros((size,size))
grid_next = np.zeros((size,size))
dVAL = 0.1

def laplaceVAL(x, y, grid):

    sum = 0

    sum += grid[x][y] * -1

    sum += grid[x-1][y] * 0.2
    sum += grid[x+1][y] * 0.2
    sum += grid[x][y+1] * 0.2
    sum += grid[x][y-1] * 0.2

    sum += grid[x-1][y-1] * 0.05
    sum += grid[x+1][y+1] * 0.05
    sum += grid[x-1][y+1] * 0.05
    sum += grid[x+1][y-1] * 0.05

    return sum


for x in range(int(size/2-2), int(size/2+2)):
    for y in range(int(size/2-2), int(size/2+2)):
        grid[x][y] = 1

iters = 4

for iter in range(iters):

    print("ITER",iter)
    print(grid)
    
    for i in range(1, size-1):
        for j in range(1,size-1):

            val = grid[i][j]

            grid_next[i][j] = val + dVAL * laplaceVAL(i,j, grid)

    grid = grid_next    


