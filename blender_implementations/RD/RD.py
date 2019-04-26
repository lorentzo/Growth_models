#import bpy
import numpy as np 
import copy
import bpy

#####################################################
# print grid
def print_grid(grid):

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            print(grid[i][j],end='')
        print()

# set pixel
# e.g. set_pixel(emp, x, y, width, [0.0, 0.0, 0.0, 1.0])
def set_pixel(img, x, y, width, color):

    offset = (x + int(y * width)) * 4

    for i in range(4):
        img.pixels[offset + i] = color[i]

# get pixel
def get_pixel(img, x, y, width):
    color = []
    offset = (x + y * width) * 4
    for i in range(4):
        color.append(img.pixels[offset+1])
    return color

# set pixels in grid
def set_pixels_by_grid(img, width, grid):

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            color = [grid[i][j][0], grid[i][j][1], 0.0, 1.0]
            set_pixel(img, i, j, width, color)




#####################################################

# blender UV editor texture

img = bpy.data.images['moja']
width = img.size[0] # cols
height = img.size[1] # rows


#####################################################

# params
#width = 128
#height = 128
rows = width
cols = height
generations = 2

# rd params
dA = 1
dB = 0.5
feed = 0.055
kill = 0.062

# ini grid and next grid
grid = []
next_grid = []
for i in range(rows):
    row = []
    row_next = []
    for j in range(cols):
        row.append(np.array([1.0, 0.0]))
        row_next.append(np.array([1.0,0.0]))
    grid.append(row)
    next_grid.append(row_next)

for i in range(30, 40):
    for j in range(50,60):   
        grid[i][j][1] = 1.0

# conv
def laplaceA(x,y,grid):

    sum = 0

    sum += grid[x][y][0] * -1

    sum += grid[x-1, y][0] * 0.2
    sum += grid[x, y-1][0] * 0.2
    sum += grid[x+1, y][0] * 0.2
    sum += grid[x, y+1][0] * 0.2

    sum += grid[x+1, y+1][0] * 0.05
    sum += grid[x-1, y-1][0] * 0.05
    sum += grid[x+1, y-1][0] * 0.05
    sum += grid[x-1, y+1][0] * 0.05

    return sum

def laplaceB(x,y,grid):

    sum = 0

    sum += grid[x][y][1] * -1

    sum += grid[x-1, y][1] * 0.2
    sum += grid[x, y-1][1] * 0.2
    sum += grid[x+1, y][1] * 0.2
    sum += grid[x, y+1][1] * 0.2

    sum += grid[x+1, y+1][1] * 0.05
    sum += grid[x-1, y-1][1] * 0.05
    sum += grid[x+1, y-1][1] * 0.05
    sum += grid[x-1, y+1][1] * 0.05

    return sum



# perform r-d
for g in range(20):
    print(g)

    for i in range(1, rows-1):
        for j in range(1, cols-1):

            a = grid[i][j][0]
            b = grid[i][j][1]

            next_grid[i][j][0] = a + (dA * laplaceA(i,j,grid) - a * b * b + feed * (1-a) ) 

            next_grid[i][j][1] = b + (dB * laplaceB(i,j,grid) + a * b *b - (kill+feed) * b) 
            
            temp = copy.copy(grid)
            grid = next_grid
            next_grid = grid # not needed?


                             
    set_pixels_by_grid(img, width, next_grid)

    
