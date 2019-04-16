"""
Inspiration:
https://www.youtube.com/watch?v=x9j8QsRMPM0
"""

import bpy
import numpy as np
import bmesh
from sca import SCA

sca = SCA(root_position=[0,0,0],
          leaves_cloud_center=[10,10,10],
          leaves_spread=[5,5,5],
          n_leaves=30,
          growth_dist={"min":0.5,"max":4})

sca.grow()

bm = bmesh.new()

for branch in sca.branches:
    if branch.parent == None:
        continue
    v1 = bm.verts.new(branch.position)
    v2 = bm.verts.new(branch.parent.position)
    bm.edges.new((v1,v2))
    
# add a new mesh data
sca_data = bpy.data.meshes.new("sca_data")  

# add a new empty mesh object using the mesh data
sca_object = bpy.data.objects.new("sca_object", sca_data) 

# make the bmesh the object's mesh
# transfer bmesh data do mesh data which is connected to empty mesh object
bm.to_mesh(sca_data)
bm.free()

# get scene
scene = bpy.context.scene

# add object to scene in
scene.objects.link(sca_object) 

for leaf in sca.leaves:
    bpy.ops.mesh.primitive_uv_sphere_add(location=leaf.position, size=0.2)


"""
# create plate 
tree_root = (0.0,0.0,0.0)
bpy.ops.mesh.primitive_plane_add(location=tree_root)
plane_obj = bpy.context.object
plane_obj.name = "tree"


# collaps plane into one vertex
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.merge(type='COLLAPSE')

# start adding
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(1,1,1)})
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(3,3,3)})

# change origin of adding
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
"""