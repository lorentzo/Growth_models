""" **********************************************************************************
IMPORTS
*********************************************************************************** """
import numpy as np
import time 
import matplotlib.pyplot as plt
import time 
import argparse
import copy
import os

""" **********************************************************************************
IMPROVE:

    FEATURES:
        + color different clusters
        + create video using plate matrices in time
        
********************************************************************************** """

""" ***********************************************************************************
CLASS
lattice EDEN model implementation
Start from arbitrary number of cells 
4-neigh growth
************************************************************************************* """

class EDEN:

    """ ******************************************************************************
    CONSTRUCTOR
    plate_size: [x_max, y_max]
    n_iter: scalar
    starters: [[x01, y01], [x02, y02], ....]
    ******************************************************************************* """
    def __init__(self, plate_size, n_iter, starters, talk, out_folder, checkpoint):

        "User specified variables"
        self.plate_size = plate_size
        self.n_iter = n_iter
        self.starters = starters
        self.talk = talk
        self.out_folder = out_folder
        self.checkpoint = checkpoint

        "Additional variables"
        self.plate = np.zeros(self.plate_size)
        self.populated = []
        for starter in self.starters:
            self.plate[starter[0]][starter[1]] = 1
            self.populated.append([starter[0], starter[1]])

        self.plates_through_iteration = []

        
    """ ***************************************************************************
    PRIVATE
    Helper function: finds free slots around populated cells, 4-neigh
    ***************************************************************************** """
    def find_grow_sites(self):

        found_grow_sites = set()

        "check around populated cells"
        for cell in self.populated:

            found = self.give_free_slots(cell)
            
            for cell in found:

                found_grow_sites.add(cell)

        return list(found_grow_sites)

    """ ********************************************************************************
    PUBLIC
    Helper function: find free slot around given cell
    ********************************************************************************* """
    def give_free_slots(self, cell):

        found_grow_sites = set()

        i = cell[0]
        j = cell[1]

        if self.plate[i, j+1] == 0:
            found_grow_sites.add((i, j+1))

        if self.plate[i, j-1] == 0:
            found_grow_sites.add((i, j-1))

        if self.plate[i-1, j] == 0:
            found_grow_sites.add((i-1, j))

        if self.plate[i+1, j] == 0:
            found_grow_sites.add((i+1, j))

        return list(found_grow_sites)


        """ ****************************************************************************
    PRIVATE
    Helper function: filters populated cells with no free neighbours
    ***************************************************************************** """
    def filter_populated(self):

        filtered = []

        for cell in self.populated:

            free_slots = self.give_free_slots(cell)

            if len(free_slots) > 0:

                filtered.append(cell)

        self.populated = filtered

    
    """ ********************************************************************************
    PRIVATE
    Helper function: plots populated cells. 
    Usually called when populated cells are filtered
    ******************************************************************************** """
    def plot_populated(self):

        back = np.zeros(self.plate_size)

        for cell in self.populated:

            back[cell[0]][cell[1]] = 1

        plt.imshow(back)
        plt.show()


    def create_plots(self):

        PATH = os.path.join('.', self.out_folder)
        if not os.path.exists(PATH):
            os.mkdir(PATH)

        cnt = 1
        for plate in self.plates_through_iteration:

            fig = plt.figure()
            ax = plt.subplot(111)
            ax.imshow(plate)

            out_file = os.path.join(PATH, str(cnt))
            fig.savefig(out_file)

            cnt += 1

    """ ****************************************************************************
    PUBLIC
    call to grow eden pattern
    **************************************************************************** """
    def grow_pattern(self):

        for sample in range(self.n_iter):

            "find coordinates where next cell can be spawned"
            grow_sites = self.find_grow_sites()

            "among found coordinates choose randomly one"
            next_grow_site_idx = np.random.randint(low=0, high=len(grow_sites), size=1)[0]
            next_grow_site_coord = grow_sites[next_grow_site_idx]

            "occupy chosen cell"
            self.plate[next_grow_site_coord[0]][next_grow_site_coord[1]] = 1
            self.populated.append([next_grow_site_coord[0], next_grow_site_coord[1]])

            "filter out cells in populated list with no free slots"
            self.filter_populated()

            if sample % self.checkpoint == 0:
                print("Cells:", sample, len(self.populated))
                self.plates_through_iteration.append(copy.copy(self.plate))

                if self.talk == 'y':
                    
                    # plot all populated
                    plt.imshow(self.plate)
                    plt.show()

                    # plot only populated (with free slots)
                    self.plot_populated()

        if self.talk == 'y':    
            plt.imshow(self.plate)
            plt.show()


""" *************************************************************************************
MAIN
Allow user to specify attributes in EDEN class
Create EDEN class object
Run
************************************************************************************* """            
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-plate-size",
                        help="Tuple x_max, y_max", 
                        type=str)

    parser.add_argument("-n-iter",
                        help="Scalar", 
                        type=int)

    parser.add_argument("-starters",
                        help="List x01, y01, x02, y02, ...", 
                        type=str)

    parser.add_argument("-talk",
                        help="Show plots during iterations (y/n)",
                        type=str)

    parser.add_argument("-checkpoint",
                        help="Iteration number to save the image",
                        type=int)

    parser.add_argument("-out-folder",
                        help="Folder where plots throught iterations will be stored",
                        type=str)

    args = parser.parse_args()

    plate_size = args.plate_size
    plate_size = plate_size.split(',')
    plate_size = [int(x) for x in plate_size]

    n_iter = args.n_iter

    starters = args.starters
    starters = starters.split(',')
    starters = np.array([int(x) for x in starters])
    starters = starters.reshape((-1,2))

    talk = args.talk
    out_folder = args.out_folder
    checkpoint = args.checkpoint

    print("INPUT:")
    print("Plate size:", plate_size)
    print("n iter:", n_iter)
    print("starters", starters)
    print("Talk?", talk)
    print("Out folder", out_folder)
    print("Checkpoint:", checkpoint)

    eden = EDEN(plate_size, n_iter, starters, talk, out_folder, checkpoint)
    start = time.time()
    eden.grow_pattern()
    eden.create_plots()
    end = time.time()
    print("time:", end-start, "s")

""" **************************************************************************************
ROOT
************************************************************************************** """
if __name__ == '__main__':
    main()