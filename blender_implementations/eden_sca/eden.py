#############################################################################
# DESCRIPTION:
# biofilm spreading based on Eden's growth model
#############################################################################

""" *************************************************************************
IMPORTS
************************************************************************* """

########################### STANDARD IMPORTS ################################
import bpy
import numpy as np
import os

""" *************************************************************************
CLASS
Eden's growth model. One plate, one starting position.
************************************************************************* """

class EDEN:

    """ ******************************************************************************
    CONSTRUCTOR
    plate_size: [x_max, y_max]
    n_iter: scalar
    starter: [x0, y0]
    ******************************************************************************* """
    def __init__(self, plate_size, n_iter, starter):

        # User specified variables
        self.plate_size = plate_size
        self.n_iter = n_iter
        self.starter = starter

        # Additional variables: plate and populated list (that will be filtered)
        self.plate = np.zeros(self.plate_size)
        self.populated = []
        self.plate[self.starter[0]][self.starter[1]] = 1
        self.populated.append([self.starter[0], self.starter[1]])
        # array for keeping the track of all added cells
        self.populated_all = []
        self.populated_all.append([self.starter[0], self.starter[1]])

        # Additional variables: mapping to blender
        self.blender_starter = [-self.starter[0], -self.starter[1]]
        self.mapper = {}
        for i in range(self.plate_size[0]):
            for j in range(self.plate_size[1]):
                self.mapper[(i,j)] = (self.blender_starter[0] + i, self.blender_starter[1] + j, 0)
        

    """ ***************************************************************************
    PRIVATE
    Helper function: finds free slots around populated cells, 4-neigh
    ***************************************************************************** """
    def find_grow_sites(self):

        found_grow_sites = set()

        # check around populated cells
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



    """ ****************************************************************************
    PUBLIC
    call to grow eden pattern
    **************************************************************************** """
    def grow(self):

        for sample in range(self.n_iter):

            # find coordinates where next cell can be spawned
            grow_sites = self.find_grow_sites()

            # among found coordinates choose randomly one
            next_grow_site_idx = np.random.randint(low=0, high=len(grow_sites), size=1)[0]
            next_grow_site_coord = grow_sites[next_grow_site_idx]

            # occupy chosen cell
            self.plate[next_grow_site_coord[0]][next_grow_site_coord[1]] = 1
            self.populated.append([next_grow_site_coord[0], next_grow_site_coord[1]])
            self.populated_all.append([next_grow_site_coord[0], next_grow_site_coord[1]])

            # filter out cells in populated list with no free slots
            self.filter_populated()


    """ ****************************************************************************
    PUBLIC HELPER FUNCTION
    using blender mesh display growth for specific iteration
    NOTE: populated_all contains all populated cells in order they were populated
    **************************************************************************** """
    def show(self, metamesh, iter):

        cell = self.populated_all[iter]

        # move metaball in direction of new cell
        element = metamesh.elements.new()
        element.co = self.mapper[(cell[0], cell[1])]
        element.radius = 2

