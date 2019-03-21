""" ************************************************************************************
IMPORTS
************************************************************************************ """
############################### STANDARD IMPORTS #######################################
import numpy as np 
import matplotlib.pyplot as plt
import argparse
import copy
import os
import time

############################### USER LIBRARIES #########################################
from img_to_video import images_to_video

""" ************************************************************************************
IMPROVE:

    FEATURES:
        + multiple attractors
        + inside circle attractor, triangle attractor, more attractors (functions, shapes...)
        + attractors scale with user input

    INFRASTRUCTURE:
        + file breakdown
************************************************************************************** """

""" ************************************************************************************
CLASS
Implementation of lattice-DLA
ATTRACTORS: one particle, outside circle, line
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
    def __init__(self, 
                plate_size, 
                starter, 
                n_particles, 
                attractor,
                radius_spawn, 
                radius_kill, 
                radius_jump, 
                talk,
                checkpoint,
                out_folder
                ):

        # User specified variables
        self.radius_spawn = radius_spawn
        self.radius_spawn_squared = np.power(self.radius_spawn, 2)

        self.radius_kill = radius_kill
        self.radius_kill_squared = np.power(self.radius_kill, 2)

        self.radius_jump = radius_jump
        self.radius_jump_squared = np.power(self.radius_jump, 2)

        self.n_particles = n_particles
        self.plate_size = plate_size
        self.starter = starter
        self.attractor = attractor

        self.talk = talk
        self.checkpoint = checkpoint
        self.out_folder = out_folder

        # Additional variables
        self.plate = np.zeros(self.plate_size)
        self.plate[self.starter[0]][self.starter[1]] = 1
        self.set_attractors(self.attractor)

        self.occupied = []
        self.occupied.append(self.starter)

        self.plate_states = []
    
    """ *******************************************************
    PRIVATE
    initialise arbitrary shape
    *********************************************************** """
    def set_attractors(self, attractor):

        if attractor == 'circle':
            self.set_attractor_circle()

        if attractor == 'line':
            self.set_attractor__line()

    """ ***************************************************
    PRIVATE
    Helper function to initial_condition()
    draws circle
    TODO: scale with user specified values
    ******************************************************* """
    def set_attractor_circle(self):

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
    def set_attractor__line(self):

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

        # spawn potential partice on circle around starter particle
        potential_particle = self.random_spawn_on_circle(self.starter)
        
        while not self.close_to_neighbour(potential_particle):

            # perform random movement
            rand_direction = np.random.randint(1, 5, 1)[0]

            if rand_direction == 1:
                potential_particle[0] += 1
            
            if rand_direction == 2:
                potential_particle[0] -= 1

            if rand_direction == 3:
                potential_particle[1] += 1

            if rand_direction == 4:
                potential_particle[1] -= 1

            # calculate distance from starter
            radius = np.power((potential_particle[0] - self.starter[0]), 2) + \
                 np.power((potential_particle[1] - self.starter[1]), 2)

            while radius > self.radius_jump_squared:

                # too far away. Spawn partice on circle around starter particle
                if radius > self.radius_kill_squared:
                    potential_particle = self.random_spawn_on_circle(self.starter)

                else:
                    # perform fast movement around itself
                    potential_particle = self.random_spawn_on_circle(potential_particle)

                # again, calculate distance from starter
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

        # draw randomly chosen pixels on circle for test
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

    """ *****************************************************************
    Private function
    Stores plots as images in folder
    ***************************************************************** """
    def store_plots(self):

        cnt = 0
        PATH = os.path.join('.', self.out_folder)
        if not os.path.exists(PATH):
            os.mkdir(PATH)

        for plate in self.plate_states:

            cnt += 1    

            fig = plt.figure()
            ax = plt.subplot(111)
            ax.imshow(plate)

            out_file = os.path.join(PATH, str(cnt))
            fig.savefig(out_file)

        # create video from images
        img_path = os.path.join('.', self.out_folder)
        video_path = os.path.join('.', self.out_folder)
        images_to_video(img_path, video_path)

    """ ***********************************************************
    Public function
    Call to run the creation of DLA pattern
    ********************************************************** """
    def create_dla_pattern(self):

        # for every paticle
        for particle in range(self.n_particles):

            # find position in dla pattern
            dla_point = self.calculate_new_dla_point()
    
            # mark position on plate
            self.plate[dla_point[0]][dla_point[1]] = 1

            if particle % self.checkpoint == 0:

                # number of particles aggregated
                print("Particles:", particle)

                # save current state of the plate
                self.plate_states.append(copy.copy(self.plate))

                # plot current state of the plate
                if self.talk == 'y':
                    plt.imshow(self.plate)
                    plt.show()

        # draw the plate
        if self.talk == 'y':
            plt.imshow(self.plate)
            plt.show()


""" ****************************************************************************
MAIN
Configure and run
**************************************************************************** """
def main():

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-plate-size",
                        help="Tuple: x_max,y_max",
                        type=str)

    parser.add_argument("-starter",
                        help="Tuple: x,y",
                        type=str)

    parser.add_argument("-attractor",
                        help="none, circle, line",
                        type=str)

    parser.add_argument("-n-iter",
                        help="Scalar",
                        type=int)

    parser.add_argument("-r-spawn",
                        help="Scalar, radius of circle where particles are spawned",
                        type=int)

    parser.add_argument("-r-kill",
                        help="Scalar, radius of circle where if outside particles are respawned",
                        type=int)

    parser.add_argument("-r-jump",
                        help="Scalar, radius of circle where if outside particles are moving fast",
                        type=int)

    parser.add_argument("-talk",
                        help="show plots after some iterations (y/n)",
                        type=str)

    parser.add_argument("-checkpoint",
                        help="iteration number where plots will be stored",
                        type=int)

    parser.add_argument("-out-folder",
                        help="folder where plots throught iterations will be stored",
                        type=str)


    args = parser.parse_args()

    plate_size = args.plate_size
    plate_size = plate_size.split(',')
    plate_size = [int(x) for x in plate_size]

    starter = args.starter
    starter = starter.split(',')
    starter = [int(x) for x in starter]

    n_iter  = args.n_iter

    radius_spawn = args.r_spawn
    radius_kill = args.r_kill
    radius_jump = args.r_jump
    attractor = args.attractor

    talk = args.talk
    out_folder = args.out_folder
    checkpoint = args.checkpoint

    print("INPUT:")
    print("Plate size:", plate_size)
    print("starter:", starter)
    print("N iter:", n_iter)
    print("Radius spawn:", radius_spawn)
    print("Radius kill:", radius_kill)
    print("Radius jump:", radius_jump)
    print("Attractor:", attractor)
    print("Talk:", talk)
    print("Out folder:", out_folder)
    print("Checkpoint:", checkpoint)

    dla = DLA(
            plate_size, 
            starter, 
            n_iter, 
            attractor,
            radius_spawn, 
            radius_kill, 
            radius_jump, 
            talk,
            checkpoint,
            out_folder
            )

    start = time.time()
    dla.create_dla_pattern()
    end = time.time()

    print("Duration:", end-start)

    dla.store_plots()

""" ****************************************************************************
ROOT
**************************************************************************** """
if __name__ == '__main__':
    main()



