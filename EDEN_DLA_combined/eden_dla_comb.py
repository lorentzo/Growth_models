
""" ****************************************************************************
IMPORTS
**************************************************************************** """

############################## STANDARD LIBRARIES ##############################
import numpy as np
import matplotlib.pyplot as plt

############################## USER LIBRARIES ##################################
from eden_lattice import EDEN
from dla_lattice import DLA

""" ****************************************************************************
CLASS
EDEN and DLA pattern formation on same plate
Colors agreement: 
    + EDEN: plate: 0, cells: 1
    + DLA: plate: 0, cells: 2, test: 3
**************************************************************************** """
class DLA_EDEN:

    """ ***********************************************************************************
    CONSTRUCTOR
    plate_size: [x_max, y_max]
    n_iter: scalar
    starter: [x,y]
    dla_attractor: 'circle', 'line', 'none'
    radius_spawn, radius_kill, radius_jump: scalars
    NOTE: radius_jump > radius spawn, radius_kill > radius_jump
    NOTE: if not 'eden' or 'dla' in variable name then it is common for both eden and dla
    *********************************************************************************** """
    def __init__(self, 
                 plate_size, 
                 eden_n_iter,
                 dla_n_iter, 
                 starter, 
                 dla_attractor,
                 dla_radius_spawn, 
                 dla_radius_kill, 
                 dla_radius_jump):

                 # user specified variables
                 self.plate_size = plate_size
                 self.dla_n_iter = dla_n_iter
                 self.eden_n_iter = eden_n_iter
                 self.starter = starter
                 self.dla_attractor = dla_attractor
                 self.dla_radius_jump = dla_radius_jump
                 self.dla_radius_kill = dla_radius_kill
                 self.dla_radius_spawn = dla_radius_spawn

                 # additional variables
                 self.plate = np.zeros(self.plate_size)


    """ **************************************************************************************
    PUBLIC
    creates EDEN and DLA pattern on same plate
    ************************************************************************************** """
    def create_pattern(self):

        # initialise EDEN model
        eden = EDEN(self.plate, 
                    self.eden_n_iter, 
                    self.starter)

        # fill plate with EDEN pattern
        eden.grow_pattern()

        # initialise DLA model
        dla = DLA(self.plate, 
                  self.dla_n_iter, 
                  self.starter, 
                  self.dla_attractor,
                  self.dla_radius_spawn, 
                  self.dla_radius_kill,
                  self.dla_radius_jump)

        # fill plate with DLA pattern
        dla.grow_pattern()


""" ***********************************************************************************
MAIN
User specify configuration
Run pattern formation
*********************************************************************************** """
def main():

    # configure pattern formation
    dla_eden = DLA_EDEN([500,500], 3000, 500, [250,250], 'none', 80, 120, 100)

    # grow pattern
    dla_eden.create_pattern()

""" *************************************************************************************
ROOT
************************************************************************************* """
if __name__ == '__main__':
    main()