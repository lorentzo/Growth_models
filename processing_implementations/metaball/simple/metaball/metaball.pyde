
class Blob:
    
    def __init__(self, pos, radius, vel):
        self.pos = pos
        self.radius = radius
        self.vel = vel
        
    def show(self):
        noFill()
        stroke(0)
        strokeWeight(4)
        ellipse(self.pos.x, self.pos.y, self.radius*2, self.radius*2)
        
    def update(self):
        self.pos.add(self.vel)
        
        if self.pos.x > width or self.pos.x < 0:
            self.vel.x *= -1
        if self.pos.y > height or self.pos.y < 0:
            self.vel.y *= -1
        
        """
        if self.pos.x > width:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = width
            
        if self.pos.y > height:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = height
        """
        
        
    
blobs = []
scl = 300
            
def setup():
    
    global blobs
    
    size(500, 200)
    
    for i in range(2):
        vel = PVector.random2D()
        vel.mult(random(10,15))
        blobs.append(Blob(PVector.random2D(), 30, vel))
    
def draw():
    
    global blobs
    
    background(55)
    
    loadPixels()
    
    for x in range(width):
        for y in range(height):
            idx = x + y * width
            sum = 0
            for blob in blobs:
                d = dist(x,y,blob.pos.x,blob.pos.y)
                if d != 0:
                    sum += scl * blob.radius / d
            pixels[idx] = color(sum)
                
    updatePixels()
    
    for blob in blobs:
        blob.update()
        #blob.show()
    
