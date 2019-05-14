


class Particle:
    
    def __init__(self):
        self.pos = [random(width),random(height)]
        self.vel = [0,0]
        self.acc = [0,0]
        self.max_vel = 2
        
    def update(self):
        self.vel[0] += self.acc[0]
        self.vel[1] += self.acc[1]
        
        if self.vel[0] > self.max_vel:
            self.vel[0] = self.max_vel
        if self.vel[1] > self.max_vel:
            self.vel[1] = self.max_vel
    
        if self.vel[1] < -self.max_vel:
            self.vel[1] = -self.max_vel
        
        if self.vel[0] < -self.max_vel:
            self.vel[0] = -self.max_vel
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        # reset
        self.acc = [0,0]
        
    def apply_force(self, force):
        self.acc[0] += force[0]
        self.acc[1] += force[1]
        
    def show(self):
        stroke(0)
        strokeWeight(4)
        point(self.pos[0], self.pos[1])
        
    def edges(self):
        if self.pos[0] > width:
            self.pos[0] = 0
        if self.pos[0] < 0:
            self.pos[0] = width
            
        if self.pos[1] > height:
            self.pos[1] = 0
        if self.pos[1] < 0:
            self.pos[1] = height
            
            
    def follow(self, field, cell_scale, cols):
        
        x = floor(self.pos[0] / cell_scale)
        y = floor(self.pos[1] / cell_scale)
        idx = x + y * cols
        force = field[idx]
        self.apply_force(force)
        

# resolution of "pixel" (rectange)
cell_scale = 10

# noise argument increase per pixel
increase = 0.1 

# "pixel  grid"
rows = 0
cols = 0

# noise z offset
z_off = 0

# particels
n_particles = 100
particles = []

# flow field
flow_field = {}

        

def setup():
    
    global rows
    global cols
    global particles
    global n_particles
    
    size(400,400)
    cols = floor(width / cell_scale)
    rows = floor(height / cell_scale)
    
    for i in range(n_particles):
        particles.append(Particle())
        
    #noLoop()
    
    
def draw():
    
    background(192, 64, 0)
    
    global rows
    global cols
    global cell_scale
    global z_off
    global particles
    global n_particles
    global flow_field
    
    # noise argument
    y_off = 0 
    
    for y in range(0,rows+1):
        
        # noise argument
        x_off = 0
        
        for x in range(0,cols+1):
            
            # positions for given resolution
            x_temp = x * cell_scale
            y_temp = y * cell_scale
            
            # 2d noise vector
            angle = noise(x_off, y_off, z_off) * TWO_PI
            
            # origin: 0,0. Destination: cos(angle), sin(angle) scaled
            noise_vector = [cos(angle) * cell_scale, sin(angle) * cell_scale]
            
            # idx of "pixel"; unscaled origin of vector
            idx = x + y * cols
            
            # save flow field
            flow_field[idx] = [cos(angle), sin(angle)]
            
            # vector
            stroke(0,50)
            strokeWeight(1)
            line(x_temp, y_temp, x_temp + noise_vector[0], y_temp + noise_vector[1])
            
            # noise argument
            x_off += increase
            
            
        # noise argument
        y_off += increase
        
    z_off += 0.01
    
    for i in range(n_particles):
        particles[i].follow(flow_field, cell_scale, cols)
        particles[i].update()
        particles[i].show()
        particles[i].edges()
        
