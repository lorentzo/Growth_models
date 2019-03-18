import numpy as np 
import matplotlib.pyplot as plt

""" ************************************************************************************
CLASS
Implementation of lattice-DLA
INITIAL CONDITION: one particle, circle around particle
Spawning area is circle
4 - neighbourhood is used
************************************************************************************** """ 
class DLA:

    """ **********************************************************************
    Constructor
    plate_size: [max_x, max_y]
    starter: [x,y]
    n_particles, radius_spawn, radius_kill, radius_jump: scalars
    NOTE: radius_jump > radius spawn, radius_kill > radius_jump
    ********************************************************************** """
    def __init__(self, plate_size, starter, n_particles, radius_spawn, radius_kill, radius_jump):

        "User specified variables"
        self.radius_spawn = radius_spawn
        self.radius_spawn_squared = np.power(self.radius_spawn, 2)

        self.radius_kill = radius_kill
        self.radius_kill_squared = np.power(self.radius_kill, 2)

        self.radius_jump = radius_jump
        self.radius_jump_squared = np.power(self.radius_jump, 2)

        self.n_particles = n_particles
        self.plate_size = plate_size
        self.starter = starter

        "Additional variables"
        self.plate = np.zeros(self.plate_size)
        self.plate[self.starter] = 1
        self.initial_condition('line')

        self.occupied = []
        self.occupied.append(np.array(self.starter))

    
    """ *******************************************************
    PRIVATE
    initialise arbitrary shape
    *********************************************************** """
    def initial_condition(self, condition):

        if condition == 'circle':
            self.inital_condition_circle()

        if condition == 'line':
            self.initial_condition_line()

    """ ***************************************************
    PRIVATE
    Helper function to initial_condition()
    draws circle
    TODO: scale with user specified values
    ******************************************************* """
    def inital_condition_circle(self):

        for sample in range(100):

            t = np.random.uniform() * 2 * np.pi
            x = int(self.starter[0] + 10 * np.sin(t))
            y = int(self.starter[1] + 10 * np.cos(t))

            self.plate[x][y] = 1

    """ ***************************************************
    PRIVATE
    Helper function to initial_condition()
    draws line 
    TODO: scale with user specified values
    ******************************************************* """
    def initial_condition_line(self):

        cnt_line = 1

        for sample in range(40):

            if sample % 2 == 1:
                self.plate[self.starter[0]][self.starter[1]+cnt_line] = 1

            else:
                self.plate[self.starter[0]][self.starter[1]-cnt_line] = 1

            cnt_line += 1


    """ ****************************************************
    Private method
    Called by create_dla_pattern() function
    Calculates point on dla pattern
    NOTE: 1: x++, 2: x--, 3: y++, 4: y--
    ***************************************************** """
    def calculate_new_dla_point(self):

        "spawn potential partice on circle around starter particle"
        potential_particle = self.random_spawn_on_circle(self.starter)
        
        while not self.close_to_neighbour(potential_particle):

            "perform random movement"
            rand_direction = np.random.randint(1, 5, 1)[0]

            if rand_direction == 1:
                potential_particle[0] += 1
            
            if rand_direction == 2:
                potential_particle[0] -= 1

            if rand_direction == 3:
                potential_particle[1] += 1

            if rand_direction == 4:
                potential_particle[1] -= 1

            "calculate distance from starter"
            radius = np.power((potential_particle[0] - self.starter[0]), 2) + \
                 np.power((potential_particle[1] - self.starter[1]), 2)

            while radius > self.radius_jump_squared:

                "too far away. Spawn partice on circle around starter particle"
                if radius > self.radius_kill_squared:
                    potential_particle = self.random_spawn_on_circle(self.starter)

                else:
                    "perform fast movement around itself"
                    potential_particle = self.random_spawn_on_circle(potential_particle)

                "again, calculate distance from starter"
                radius = np.power((potential_particle[0] - self.starter[0]), 2) + \
                    np.power((potential_particle[1] - self.starter[1]), 2)

        return potential_particle
        

    """ *************************************************************
    Private function
    return random point on circle arund given point for given radius
    *************************************************************** """
    def random_spawn_on_circle(self, center):

        t = np.random.uniform() * 2 * np.pi
        x = int(self.starter[0] + self.radius_spawn * np.sin(t))
        y = int(self.starter[0] + self.radius_spawn * np.cos(t))

        "draw randomly chosen pixels on circle for test"
        self.plate[x][y] = 2

        return [x,y]


    """ *****************************************************************
    Private function
    For given particle postion look around 4-neigh for neighbours
    ***************************************************************** """
    def close_to_neighbour(self, particle):

        if self.plate[particle[0] + 1, particle[1]] == 1:
            return True
        
        if self.plate[particle[0] - 1, particle[1]] == 1:
            return True

        if self.plate[particle[0], particle[1] + 1] == 1:
            return True

        if self.plate[particle[0], particle[1] - 1] == 1:
            return True

        return False

    """ ***********************************************************
    Public function
    Call to run the creation of DLA pattern
    ********************************************************** """
    def create_dla_pattern(self):

        "for every paticle"
        for particle in range(self.n_particles):

            "find position in dla pattern"
            dla_point = self.calculate_new_dla_point()
    
            "mark position on plate"
            self.plate[dla_point[0]][dla_point[1]] = 1

            if particle % 100 == 0:
                print("Particles:", particle)

        "draw the plate"
        plt.imshow(self.plate)
        plt.show()

def main():

    dla = DLA((1000,1000), (500,500), 1000, 100, 130, 120)

    dla.create_dla_pattern()

if __name__ == '__main__':
    main()



