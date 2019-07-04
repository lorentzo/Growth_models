
#
# This source file is part of Growth_models.
# Visit https://github.com/lorentzo/Growth_models for more information.
#
# This software is released under MIT licence.
#
# Copyright (c) Lovro Bosnar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

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

        # Additional variables: plate 
        self.plate = np.zeros(self.plate_size)
        self.plate[self.starter[0]][self.starter[1]] = 1
        
        # populated list (that will be filtered)
        self.populated = []
        self.populated.append([self.starter[0], self.starter[1]])

        # populated list for keeping the track of all added cells
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
    Helper function: find free slot around given cell (4-neigh)
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

        return filtered



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
            self.population = self.filter_populated()



