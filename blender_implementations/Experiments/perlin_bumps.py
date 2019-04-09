import bpy
import numpy as np
from mathutils import noise

# add plane mesh
bpy.ops.mesh.primitive_cube_add()
plane = bpy.context.object
plane.name = 'air_plane'

# select plane
plane = bpy.data.objects['air_plane']

# enter edit mode
bpy.ops.object.mode_set(mode='EDIT')

# subdivide
bpy.ops.mesh.subdivide(number_cuts=10)

# get vertices
bpy.ops.mesh.select_mode(type='VERT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT') # pazi!!

verts = plane.data.vertices
print("N", len(verts))
for v in verts:
    v.co[1] = noise.noise(v.co)

