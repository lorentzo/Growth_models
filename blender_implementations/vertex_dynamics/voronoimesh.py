import bpy
import bmesh
import numpy as np
from Voronoi import Voronoi

radius = 5
n_points = 200

points = []

for i in range(n_points):

    found = False
    while not found:

        point = np.random.rand(2) * radius

        if np.random.rand() > 0.5:
            point[1] *= -1

        if np.random.rand() > 0.5:
            point[0] *= -1

        if np.linalg.norm(point) < radius:
            points.append(point)
            found = True

vp = Voronoi(points)
vp.process()
lines = vp.get_output()

bm = bmesh.new()
for point in points:
    bm.verts.new([point[0], point[1], 0])

lines = sorted(lines, key=lambda x: np.linalg.norm(x))
cnt = 0
for line in lines:
    if cnt > 100:
        break
    if np.linalg.norm(line) > 10:
        continue
    p1 = bm.verts.new([line[0], line[1],0])
    p2 = bm.verts.new([line[2], line[3],0])
    bm.edges.new([p1,p2])
    cnt += 1

mesh_data = bpy.data.meshes.new("mesh_data")
mesh_obj = bpy.data.objects.new("mesh_obj", mesh_data)
bm.to_mesh(mesh_data)
bm.free()

scene = bpy.context.scene
scene.objects.link(mesh_obj)

