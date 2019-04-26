
def diffuse(x, y, grid):

    sum = 0

    sum += grid[x][y] * 1

    sum += grid[x-1][y] * 0.2
    sum += grid[x+1][y] * 0.2
    sum += grid[x][y+1] * 0.2
    sum += grid[x][y-1] * 0.2

    sum += grid[x-1][y-1] * 0.05
    sum += grid[x+1][y+1] * 0.05
    sum += grid[x-1][y+1] * 0.05
    sum += grid[x+1][y-1] * 0.05

    return sum

grid = []
grid_next = []
grid_b = []
dVAL = 1
f = 0.54

def setup():
    
    size(500,500)
    
    global grid
    global grid_next
    global grid_b
    
    for x in range(1, width):
        row = []
        row_next = []
        row_b = []
        for y in range(1, height):
            row.append(0)
            row_next.append(0)
            row_b.append(0)
        grid.append(row)
        grid_next.append(row_next)
        grid_b.append(row_b)
        
        

    for x in range(-30 + width/2, width/2 + 30):
        for y in range(-30 + height/2, height/2 + 30):
            grid[x][y] = random(0,1)

    
    grid[width/2][height/2] = 1
    
    for x in range(10,width-10):
        for y in range(10,height-10):
            grid_b[x][y] = random(0,0.1)

    
             
cnt = 0
def draw():
    
    global grid
    global grid_next
    global grid_b
    global dVAL
    global cnt
    global f
    
    background(44)
    
    loadPixels()
    
    cnt+=1
    print(cnt)
    
    for x in range(10,width-10):
        for y in range(10,height-10):
            
            val = grid[x][y]
            b = grid_b[x][y]
            b = random(0, 0.2)
            
            grid_next[x][y] = val + ( dVAL * diffuse(x,y,grid) - b * b * f * (1-val) )
            
            idx = x + y * width
            pixels[idx] = color(grid_next[x][y] * 255)
            
    grid = grid_next
            
    updatePixels()
