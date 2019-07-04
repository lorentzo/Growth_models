
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

import numpy as np 
import bpy
import os



class Cell:

    def __init__(self, position, normal, neigh_topology, size):

        self.position = np.array(position)
        self.normal = np.array(normal)
        self.size = size

        self.nutrient_level = 0
        self.nutrient_tresh = 5
        self.nutrient_delta = 1

        self.neigh_topology = neigh_topology

        bpy.ops.mesh.primitive_uv_sphere_add(location=self.position, size=self.size)
        self.blender_sphere = bpy.context.object


    def increase_nutrient(self):

        self.nutrient_level += self.nutrient_delta

        if self.nutrient_level == self.nutrient_tresh:

            self.nutrient_level = 0

            return True
        
        return False


    
class organism:

    def __init__(
        self, 
        link_resistance,
        spring_facor,
        planar_factor,
        bulge_factor
        ):

        self.cells, self.cells_m = self.init_cells()
        self.link_resistance = link_resistance
        self.spring_factor = spring_facor
        self.planar_factor = planar_factor
        self.bulge_factor = bulge_factor


    def init_cells(self):
        
        cell_matrix = []
        n_cells = 8
        pos_x = 0
        pos_y = 0
        x_dist = 0.1
        y_dist = 0.1

        for i in range(n_cells):
            cells = []
            pos_x += x_dist
            pos_y = 0
            for j in range(n_cells):
                pos_y += y_dist
                cell = Cell(np.array([pos_x, pos_y, 0]), [0,0,1.0], None, 0.1)
                cells.append(cell)
            cell_matrix.append(cells)

        cell_list = []

        for i in range(1, n_cells-1):
            for j in range(1, n_cells-1):
                cell = cell_matrix[i][j]
                cell_list.append(cell)
                topology = []
                topology.append(cell_matrix[i][j+1])
                topology.append(cell_matrix[i][j-1])
                topology.append(cell_matrix[i+1][j])
                topology.append(cell_matrix[i-1][j])
                topology.append(cell_matrix[i-1][j-1])
                topology.append(cell_matrix[i-1][j+1])
                topology.append(cell_matrix[i+1][j-1])
                topology.append(cell_matrix[i+1][j+1])
                cell.neigh_topology = topology

        for i in range(1, n_cells-1):
            j = 0
            cell = cell_matrix[i][j]
            cell_list.append(cell)
            topology = []
            topology.append(cell_matrix[i-1][j])
            topology.append(cell_matrix[i+1][j])
            topology.append(cell_matrix[i-1][j])
            topology.append(cell_matrix[i+1][j+1])
            topology.append(cell_matrix[i][j+1])
            cell.neigh_topology = topology

        for i in range(1, n_cells-1):
            j = n_cells-1
            cell = cell_matrix[i][j]
            cell_list.append(cell)
            topology = []
            topology.append(cell_matrix[i+1][j-1])
            topology.append(cell_matrix[i+1][j])
            topology.append(cell_matrix[i-1][j-1])
            topology.append(cell_matrix[i-1][j])
            topology.append(cell_matrix[i][j-1])
            cell.neigh_topology = topology

        for j in range(1, n_cells-1):
            i = 0
            cell = cell_matrix[i][j]
            cell_list.append(cell)
            topology = []
            topology.append(cell_matrix[i+1][j+1])
            topology.append(cell_matrix[i+1][j-1])
            topology.append(cell_matrix[i+1][j-1])
            topology.append(cell_matrix[i][j+1])
            topology.append(cell_matrix[i][j-1])
            cell.neigh_topology = topology

        for j in range(1, n_cells-1):
            i = n_cells-1
            cell = cell_matrix[i][j]
            cell_list.append(cell)
            topology = []
            topology.append(cell_matrix[i-1][j+1])
            topology.append(cell_matrix[i-1][j-1])
            topology.append(cell_matrix[i-1][j])
            topology.append(cell_matrix[i][j+1])
            topology.append(cell_matrix[i][j-1])
            cell.neigh_topology = topology

        i = 0
        j = 0
        cell = cell_matrix[0][0]
        cell_list.append(cell)
        topology = []
        topology.append(cell_matrix[i+1][j+1])
        topology.append(cell_matrix[i][j+1])
        topology.append(cell_matrix[i+1][j])
        cell.neigh_topology = topology

        i = n_cells-1
        j = 0
        cell = cell_matrix[n_cells-1][0]
        cell_list.append(cell)
        topology = []
        topology.append(cell_matrix[i-1][j+1])
        topology.append(cell_matrix[i][j+1])
        topology.append(cell_matrix[i-1][j])
        cell.neigh_topology = topology

        i = n_cells-1
        j = n_cells-1
        cell = cell_matrix[i][j]
        cell_list.append(cell)
        topology = []
        topology.append(cell_matrix[i-1][j])
        topology.append(cell_matrix[i][j-1])
        topology.append(cell_matrix[i-1][j-1])
        cell.neigh_topology = topology

        i = 0
        j = n_cells-1
        cell = cell_matrix[0][n_cells-1]
        cell_list.append(cell)
        topology = []
        topology.append(cell_matrix[i+1][j])
        topology.append(cell_matrix[i][j-1])
        topology.append(cell_matrix[i+1][j-1])
        cell.neigh_topology = topology

        return cell_list, cell_matrix

            


    def test_topology(self, i, j):
        cell = self.cells_m[i][j] 
        for nc in cell.neigh_topology:
            bpy.ops.mesh.primitive_cube_add(location=nc.position, size=0.1)

               
    def constant_distance_force(self, cell):

        sum_spring = 0
        for cell_neigh in cell.neigh_topology:
            dist = cell.position - cell_neigh.position
            dist_norm = dist / np.linalg.norm(dist)
            sum_spring += cell_neigh.position + self.link_resistance * dist_norm

        return  sum_spring / len(cell.neigh_topology) 


    def planar_position_force(self, cell):

        sum_planar = 0
        for cell_neigh in cell.neigh_topology:
            sum_planar += cell_neigh.position

        return sum_planar / len(cell.neigh_topology)

    def bulge_force(self, cell):

        sum_bulge = 0
        for cell_neigh in cell.neigh_topology:

            dotN = np.dot((cell_neigh.position - cell.position), cell.normal)

            root_ex = self.link_resistance ** 2 - np.linalg.norm(cell_neigh.position) ** 2 + dotN ** 2
            if root_ex < 0:
                root_ex = 0

            sum_bulge += np.sqrt(root_ex) + dotN

        avg_bulge = sum_bulge / len(cell.neigh_topology)
            
        bulge = cell.position + avg_bulge * cell.normal

        return bulge

    def cell_diff(self, cell):
        x = np.random.rand() / 10
        y = np.random.rand() / 10
        z = 0
        if np.random.rand() > 0.5:
            x *= -1
        
        if np.random.rand() > 0.5:
            y *= -1
            
        new_cell = Cell(cell.position + [x,y,z], [0,0,1.0], None, 0.1)
        self.cells.append(new_cell)

        half_topology_neigh = int(len(cell.neigh_topology)/2)

        topology_for_old_cell = []
        for i in range(0, half_topology_neigh):
            topology_for_old_cell.append(cell.neigh_topology[i])

        topology_for_old_cell.append(new_cell)

        topology_for_new_cell = []
        for i in range(half_topology_neigh, len(cell.neigh_topology)):
            topology_for_new_cell.append(cell.neigh_topology[i])

        topology_for_new_cell.append(cell)

        cell.neigh_topology = topology_for_old_cell
        new_cell.neigh_topology = topology_for_new_cell




    def grow(self, n_iter):

        curr_iter = 0
        render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/cell_diff/tmp/'
        render_iter = 0

        while True:

            for cell in self.cells:

                differentiate = cell.increase_nutrient()

                if differentiate:

                    self.cell_diff(cell)

                    

            for cell in self.cells:

                spring_target = self.constant_distance_force(cell)
                planar_target = self.planar_position_force(cell)
                bulge_target = self.bulge_force(cell)

                spring = self.spring_factor * (spring_target - cell.position)
                planar = self.planar_factor * (planar_target - cell.position)
                bulge = self.bulge_factor * (bulge_target - cell.position)

                new_position = cell.position + planar + spring + bulge
    

                cell.position = new_position
                cell.blender_sphere.location = new_position

            bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
            bpy.ops.render.render(write_still=True)
            render_iter += 1

            curr_iter += 1
            if curr_iter > n_iter:
                break


org = organism(
        link_resistance = 0.4,
        spring_facor = 1,
        planar_factor = 1.1,
        bulge_factor = 0.00001
    ) 
       
org.grow(20)
bpy.ops.mesh.primitive_cone_add(location=org.cells[4].position)
bpy.context.object.scale = [0.3,0.3,0.3]
for cell_neigh in org.cells[4].neigh_topology:
    bpy.ops.mesh.primitive_cube_add(location=cell_neigh.position, radius=0.1)

