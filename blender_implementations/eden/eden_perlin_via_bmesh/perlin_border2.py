
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

from mathutils import noise
import numpy as np 
import bpy
import bmesh
import os

class Vertex:

    def __init__(self, phi, r):

        self.phi = phi
        self.r = r

    def give_position(self):

        return np.array([self.r * np.cos(self.phi), self.r * np.sin(self.phi), 0])

class PerlinCircle:


        """ ####################################################################################
        CONSTRUCTOR:
        center: np.array([xc, yc, zc])
        starting_radius: scalar -- starting radius, ending radius and step
        ##################################################################################### """
        def __init__(self,
                     center,
                     starting_radius,
                     n_starting_vertices
                    ):

                # user defined variables
                self.center = center
                self.starting_radius = starting_radius
                self.n_starting_vertices = n_starting_vertices

                self.vertices = self.init_shape()

        def init_shape(self):

            phis = np.linspace(0, 2*np.pi, self.n_starting_vertices)
            vertices = []

            for phi in phis:

                vertices.append(Vertex(phi, self.starting_radius))

            return vertices
            


        def construct_mesh(self, vertices):

            bm = bmesh.new()

            for vertex in vertices:
                bm.verts.new(vertex.give_position())

            bm.faces.new(bm.verts)

            # add a new mesh data
            layer_mesh_data = bpy.data.meshes.new("mesh_data")  

            # add a new empty mesh object using the mesh data
            layer_mesh_object = bpy.data.objects.new("mesh_object", layer_mesh_data) 

            # make the bmesh the object's mesh
            # transfer bmesh data do mesh data which is connected to empty mesh object
            bm.to_mesh(layer_mesh_data)
            bm.free()

            # add to scene
            bpy.context.scene.objects.link(layer_mesh_object)



        def grow(self, n_iter):

            for i in range(n_iter):

                vertex_idx = np.random.choice(len(self.vertices), 1)[0]

                pos = np.array([np.cos(self.vertices[vertex_idx].phi), np.sin(self.vertices[vertex_idx].phi), np.pi])

                noise_val = noise.noise(pos)

                self.vertices[vertex_idx].r += np.abs(noise_val)

            self.construct_mesh(self.vertices)


pc = PerlinCircle([0,0,0], 1, 30)
pc.grow(10)



