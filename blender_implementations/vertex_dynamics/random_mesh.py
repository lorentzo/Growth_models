
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
import bmesh

center = [0, 0, 0]
radius = 10
n_points = 500

points = []

for i in range(n_points):

    found = False
    while not found:

        point = np.random.rand(3) * radius

        point[2] = 0

        if np.random.rand() > 0.5:
            point[1] *= -1

        if np.random.rand() > 0.5:
            point[0] *= -1

        if np.linalg.norm(point) < radius:
            points.append(point)
            found = True

bm = bmesh.new()
for point in points:
    bm.verts.new(point)

mesh_data = bpy.data.meshes.new("mesh_data")
mesh_obj = bpy.data.objects.new("mesh_obj", mesh_data)
bm.to_mesh(mesh_data)
bm.free()

scene = bpy.context.scene
scene.objects.link(mesh_obj)

starter = [0,0,0]


