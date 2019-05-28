
grid = []
next = []
dA = 1.0
dB = 0.5
feed = 0.055
k = 0.062


def laplace(x,y, chem):
    
    global grid
    
    sum = 0 
    
    sum += grid[x][y][chem] * -1
    
    sum += grid[x-1][y][chem] * 0.2
    sum += grid[x][y-1][chem] * 0.2 
    sum += grid[x+1][y][chem] * 0.2
    sum += grid[x][y+1][chem] * 0.2
    
    sum += grid[x-1][y-1][chem] * 0.05
    sum += grid[x+1][y-1][chem] * 0.05
    sum += grid[x-1][y+1][chem] * 0.05
    sum += grid[x+1][y+1][chem] * 0.05
    
    return sum


def setup():
    
    global grid
    global next
    
    size(100,100)
    pixelDensity(1)
    
    grid = []
    for x in range(width):
        vector = []
        vector2 = []
        for y in range(height):
            vector.append({"a":1.0, "b":0.0})
            vector2.append({"a":1.0, "b":0.0})
        grid.append(vector)
        next.append(vector2)
            
    for i in range(50, 61):
        for j in range(50, 61):
            grid[i][j]["b"] = 1.0
    
    
def draw():
    
    global grid
    global next
    
    global dA 
    global dB 
    global feed 
    global k
        
    background(51)
    
    
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            A = grid[x][y]["a"]
            B = grid[x][y]["b"]
            next[x][y]["a"] = A + (dA * laplace(x,y,"a") - A * B ** 2 + feed * (1-A))
            next[x][y]["b"] = B + (dB * laplace(x,y,"b") + A * B ** 2 - (k + feed) * B)
    
    loadPixels()
    
    for x in range(width):
        for y in range(height):
            
            pos = x + y * width 
            
            pixels[pos] = color(next[x][y]["a"] * 255, 0, next[x][y]["b"] * 255)

            
    updatePixels()
    
    tmp = grid
    grid = next
    next = tmp
    
    
