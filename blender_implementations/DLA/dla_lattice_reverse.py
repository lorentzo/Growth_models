
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
import bmesh

class LatticeDLA:

    def __init__(
        self,
        plate_size,
        starter,
        n_particles,
        radius_spawn,
        radius_kill,
        radius_jump,
        out):

        self.radius_spawn = radius_spawn
        self.radius_kill = radius_kill
        self.radius_jump = radius_kill

        self.n_particles = n_particles
        self.plate_size = plate_size
        self.starter = starter

        self.plate = np.zeros(plate_size)
        for i in range(100):
            ini = self.spawn_particle_on_circle(self.starter, self.radius_spawn)
            print(ini)
            self.plate[ini[0]][ini[1]] = 1



    def spawn_particle_on_circle(self, center, radius):

        phi = np.random.rand() * 2 * np.pi

        x = int(center[0] + radius * np.cos(phi))
        y = int(center[1] + radius * np.sin(phi))

        return np.array([x,y])

    def is_close(self, particle):


        if self.plate[particle[0] + 1, particle[1]] == 1:
            return True
        
        if self.plate[particle[0] - 1, particle[1]] == 1:
            return True

        if self.plate[particle[0], particle[1] + 1] == 1:
            return True

        if self.plate[particle[0], particle[1] - 1] == 1:
            return True

        return False




    def find_cell(self):

        particle = self.starter
        print()

        while not self.is_close(particle):

            # random move
            rand_dir = np.random.rand()

            if rand_dir < 0.25:
                particle[0] += 1

            if rand_dir > 0.25 and rand_dir < 0.5:
                particle[0] -= 1

            if rand_dir > 0.5 and rand_dir < 0.75:
                particle[1] += 1

            if rand_dir > 0.75:
                particle[1] -= 1


        return particle

    
    def grow(self):
        
        for particle in range(self.n_particles):

            found_cell = self.find_cell()

            print(str(particle+1) + '/' + str(self.n_particles) + str(found_cell))

            self.plate[found_cell[0]][found_cell[1]] = 1
        
        
        self.display1()
        

    def display1(self):

        for i in range(self.plate_size[0]):
            for j in range(self.plate_size[1]):
                if self.plate[i][j] == 1:
                    bpy.ops.mesh.primitive_uv_sphere_add(size=0.2, location=[i-self.starter[0],j-self.starter[1],0])



def main():

    render_out='/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/dla_lattice/tmp/'

    dla = LatticeDLA(plate_size=np.array([200,200]),
                     starter=np.array([100,100]),
                     n_particles=600,
                     radius_spawn=50, 
                     radius_kill=70, 
                     radius_jump=60,
                     out=render_out)

    dla.grow()

main()

    








