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


