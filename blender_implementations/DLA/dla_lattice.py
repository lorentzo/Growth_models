
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
from colorsys import hsv_to_rgb

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
        self.plate[starter[0]][starter[1]] = 1

        self.tree = []


    def spawn_particle_on_circle(self, center, radius):

        phi = np.random.rand() * 2 * np.pi

        x = int(center[0] + radius * np.cos(phi))
        y = int(center[1] + radius * np.sin(phi))

        return np.array([x,y])

    def is_close(self, particle):


        if self.plate[particle[0] + 1, particle[1]] == 1:
            self.tree.append([[particle[0] + 1, particle[1]], particle])
            return True
        
        if self.plate[particle[0] - 1, particle[1]] == 1:
            self.tree.append([[particle[0] - 1, particle[1]], particle])
            return True

        if self.plate[particle[0], particle[1] + 1] == 1:
            self.tree.append([[particle[0], particle[1] + 1], particle])
            return True

        if self.plate[particle[0], particle[1] - 1] == 1:
            self.tree.append([[particle[0], particle[1] - 1], particle])
            return True

        return False




    def find_cell(self):

        particle = self.spawn_particle_on_circle(self.starter, self.radius_spawn)

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

            # dist from starter
            dist = np.linalg.norm(self.starter - particle)

            while dist > self.radius_jump:

                if dist > self.radius_kill:
                    particle = self.spawn_particle_on_circle(self.starter, self.radius_spawn)

                else:
                    particle = self.spawn_particle_on_circle(particle, self.radius_jump)

                dist = np.linalg.norm(self.starter - particle)

        return particle

    def display1(self):

        for i in range(self.plate_size[0]):
            for j in range(self.plate_size[1]):
                if self.plate[i][j] == 1:
                    bpy.ops.mesh.primitive_uv_sphere_add(size=0.2, location=[(i-self.starter[0]) / 5, (j-self.starter[1]) / 5,0])

    def interpolate(self, v1, v2, n_interp, amp, bm):

        helper_nodes = []

        for t in range(n_interp+1):

            x = (1 - t/n_interp) * v1.co[0] + (t/n_interp) * v2.co[0]
            y = (1 - t/n_interp) * v1.co[1] + (t/n_interp) * v2.co[1]

            x += np.random.rand() * amp
            y += np.random.rand() * amp

            helper_nodes.append(bm.verts.new([x,y,0]))

        return helper_nodes


    def display2(self):

        bm = bmesh.new()
        
        # bevel object
        bpy.ops.curve.primitive_nurbs_circle_add()
        bpy.context.object.scale = (0.1,0.1,0)
        bevel_object = bpy.context.object

        for branch in self.tree:
            
            v1 = bm.verts.new([(branch[0][0]-self.starter[0]) / 5, (branch[0][1]-self.starter[0]) / 5, 0])
            v2 = bm.verts.new([(branch[1][0]-self.starter[0]) / 5, (branch[1][1]-self.starter[0]) / 5, 0])
            
            interpolated = self.interpolate(v1, v2, 4, 0.1, bm)

            for i in range(len(interpolated)-1):
                bm.edges.new((interpolated[i], interpolated[i+1]))
            

        # create mesh object using bmesh data
        mesh_data = bpy.data.meshes.new("dla_mesh_data")
        mesh_obj = bpy.data.objects.new("dla_mesh_obj", mesh_data)
        bm.to_mesh(mesh_data)
        bm.free()

        # add mesh object to the scene
        scene = bpy.context.scene
        scene.objects.link(mesh_obj)
        
        mesh_obj.select = True
        bpy.context.scene.objects.active = mesh_obj
        bpy.ops.object.convert(target='CURVE')
        mesh_obj.data.bevel_object = bevel_object
        
        # add color
        material = bpy.data.materials.new("material")
        material.diffuse_color = hsv_to_rgb(30.0/360.0, 80.0/100.0, 80.0/100.0)
        mesh_obj.active_material = material
        
        
       

                    





    def grow(self):

        for particle in range(self.n_particles):

            found_cell = self.find_cell()

            print(str(particle+1) + '/' + str(self.n_particles))

            self.plate[found_cell[0]][found_cell[1]] = 1

        self.display2()
        

def main():

    render_out='/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/dla_lattice/tmp/'

    dla = LatticeDLA(np.array([200,200]),
                     np.array([100,100]),
                     600,
                     50, 70, 60, render_out)

    dla.grow()

main()

    








