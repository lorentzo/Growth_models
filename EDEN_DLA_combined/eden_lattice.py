
""" **********************************************************************************
IMPORTS
*********************************************************************************** """

################################# STANDARD LIBRARIES ##################################
import numpy as np
import time 
import matplotlib.pyplot as plt

""" ***********************************************************************************
CLASS
lattice EDEN model implementation
Start from ONE arbitrary cell
4-neigh growth
Colors agreement: 
    + EDEN: plate: 0, cells: 1
    + DLA: plate: 0, cells: 2, test: 3
************************************************************************************* """
class EDEN:

    """ ******************************************************************************
    CONSTRUCTOR
    plate: np.array(dim:[x_max, y_max]). Need to match DLA model
    n_iter: scalar
    starter: [x01, y01]. IN this context only one starter cell is 
                chosen which is same as stater cell in DLA model
    ******************************************************************************* """
    def __init__(self, 
                 plate,
                 n_iter, 
                 starter,
                 plate_color=0,
                 cell_color=1):

        # User specified variables
        self.n_iter = n_iter
        self.starter = starter
        self.cell_color = cell_color
        self.plate_color = plate_color
        self.plate = plate

        # Additional variables
        self.populated = []
        self.plate[self.starter[0]][self.starter[1]] = self.cell_color
        self.populated.append([self.starter[0], self.starter[1]])

        
    """ ***************************************************************************
    PRIVATE
    Helper function: finds free slots around populated cells, 4-neigh
    ***************************************************************************** """
    def find_grow_sites(self):

        found_grow_sites = set()

        "check around populated cells"
        for cell in self.populated:

                i = cell[0]
                j = cell[1]

                if self.plate[i, j+1] == self.plate_color:
                    found_grow_sites.add((i, j+1))

                if self.plate[i, j-1] == self.plate_color:
                    found_grow_sites.add((i, j-1))

                if self.plate[i-1, j] == self.plate_color:
                    found_grow_sites.add((i-1, j))

                if self.plate[i+1, j] == self.plate_color:
                    found_grow_sites.add((i+1, j))

        return list(found_grow_sites)


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
            self.plate[next_grow_site_coord[0]][next_grow_site_coord[1]] = self.cell_color
            self.populated.append([next_grow_site_coord[0], next_grow_site_coord[1]])

            if sample % 100 == 0:
                print("EDEN particles", sample)

        plt.imshow(self.plate)
        plt.show()


    """ ******************************************************************************
    PUBLIC
    Fetch created eden pattern
    ****************************************************************************** """
    def give_plate(self):
        return self.plate