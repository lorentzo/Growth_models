
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

import bpy
import numpy as np
import os

class Cell:

    def __init__(self, center, radius):

        self.center = np.array(center)
        self.radius = radius

        bpy.ops.mesh.primitive_uv_sphere_add(
            location=self.center,
            size=self.radius)
            
        bpy.context.object.select = False
        self.sobject = bpy.context.object


class Organism:

    def __init__(
        self, 
        cell_radius,
        n_cells_per_diff,
        n_iter,
        out):

        self.n_cells_per_diff = n_cells_per_diff
        self.n_iter = n_iter
        self.out = out
        self.cell_radius = cell_radius

        self.active_cells = []
        self.active_cells.append(Cell(center=[0,0,0], radius=cell_radius))

    # e.g. locations = [pi, pi/2]
    def differentiate(
        self,
        cell,
        locations):

        new_cells = []

        # for every diff location create new cell
        for location in locations:

            center_x = cell.center[0] + cell.radius * np.cos(location)
            center_y = cell.center[1] + cell.radius * np.sin(location)
            center = [center_x, center_y, 0]

            new_cells.append(Cell(center=center, radius=cell.radius))

        # remove parent cell
        cell.sobject.select = True
        bpy.ops.object.delete(use_global=False)
        
        return new_cells

    def differentiation_locations(self):

        n_new_cells = np.random.randint(low=4, high=7)

        segment = np.pi * 2 / n_new_cells + np.random.rand() * np.pi

        locations = []
        for n in range(n_new_cells):
            locations.append(segment * n+1)

        return locations


    def force_up(self, new_cells):

        for new_cell in new_cells:

            dx = 0
            dy = 0
            k = 1.3

            for cell in self.active_cells:

                dx += cell.center[0] - new_cell.center[0]
                dy += cell.center[1] - new_cell.center[1]

                if np.linalg.norm(new_cell.center-cell.center) < self.cell_radius:
                    print("!")

                    if new_cell.center[2] < self.cell_radius * 2:
                        print("!!")
                        new_cell.center[2] += self.cell_radius * np.random.rand()
                        new_cell.sobject.location = new_cell.center


            dx /= len(self.active_cells)
            dy /= len(self.active_cells)
            z = new_cell.center[2]
            new_cell.center += k * (np.array([dx,dy,0]) - new_cell.center)
            new_cell.center[2] = z
            new_cell.sobject.location = new_cell.center

            

            



    def grow(self):

        render_iter = 0

        for n in range(self.n_iter):

            updated_active_cells = []

            for cell in self.active_cells:

                diff_loc = self.differentiation_locations()

                new_cells = self.differentiate(cell, diff_loc)

                self.force_up(new_cells)

                updated_active_cells.extend(new_cells)

                bpy.context.scene.render.filepath = os.path.join(self.out, str(render_iter))
                bpy.ops.render.render(write_still=True)
                render_iter += 1

            self.active_cells = updated_active_cells

def main():

    out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/lsys/tmp/'

    org = Organism(cell_radius=0.5, n_cells_per_diff=4, n_iter=7, out=out)
    org.grow()


main()
        



    
