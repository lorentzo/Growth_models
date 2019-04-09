import bpy
import bmesh
import numpy as np 

verts = [(1, 1, 1), (0, 0, 0)]  # 2 verts made with XYZ coords

# mesh data
mesh_data = bpy.data.meshes.new("mesh")

# mesh obh
mesh_obj = bpy.data.objects.new("geometrija", mesh_data)

# get scene
scene = bpy.context.scene

# link object to scene
scene.objects.link(mesh_obj)

# active and select mesh object
scene.objects.active = mesh_obj
mesh_obj.select = True
# select 
mesh = bpy.context.object.data

# create b mesh
bm = bmesh.new()

# add vertices to bmesh
for v in verts:
    bm.verts.new(v)

# make mesh from b mesh
bm.to_mesh(mesh)
