
""" **********************************************************************************
IMPORTS
*********************************************************************************** """

################################# STANDARD LIBRARIES ##################################
import numpy as np
import matplotlib.pyplot as plt
import copy

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
                 plate_size,
                 n_iter, 
                 starter,
                 checkpoint,
                 plate_color=0,
                 cell_color=1):

        # User specified variables
        self.n_iter = n_iter
        self.starter = starter
        self.cell_color = cell_color
        self.plate_color = plate_color
        self.plate_size = plate_size
        self.checkpoint = checkpoint
        self.shoot = int(n_iter / checkpoint)

        # Additional variables
        self.plate = np.zeros(self.plate_size)
        self.populated = []
        self.plate[self.starter[0]][self.starter[1]] = self.cell_color
        self.populated.append([self.starter[0], self.starter[1]])
        self.plate_through_iterations = []

        
    """ ***************************************************************************
    PRIVATE
    Helper function: finds free slots around populated cells, 4-neigh
    ***************************************************************************** """
    def find_grow_sites(self):

        found_grow_sites = set()

        "check around populated cells"
        for cell in self.populated:

                found = self.give_free_slots(cell)

                for cell_i in found:
                    found_grow_sites.add(cell_i)

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

            "filter out cells in populated list with no free slots"
            self.filter_populated()

            if sample % self.shoot == 0:
                print("EDEN particles", sample, len(self.populated))
                self.plate_through_iterations.append(copy.copy(self.plate))



    """ ******************************************************************************
    PUBLIC
    Fetch created eden patterns
    ****************************************************************************** """
    def give_plates(self):
        return self.plate_through_iterations