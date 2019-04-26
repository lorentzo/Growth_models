"""
Inspiration:
Given SCA nodes construct b mesh, tranform b mesh to mesh
"""

import bpy
import numpy as np
import bmesh
from sca import SCA

"given two vertices insert additional vertices with noise"
def insert_helper_nodes(v1, v2, bm):
    
    helper_nodes = []
    n_nodes = 11
    rand_amplitude = 5

    for t in range(n_nodes+1):

        # interpolate
        x = (1 - t / n_nodes) * v1.co[0] + (t / n_nodes) * v2.co[0]
        y = (1 - t / n_nodes) * v1.co[1] + (t / n_nodes) * v2.co[1]
        z = (1 - t / n_nodes) * v1.co[2] + (t / n_nodes) * v2.co[2]

        # add random noise
        x += np.random.rand() / rand_amplitude
        y += np.random.rand() / rand_amplitude
        z += np.random.rand() / rand_amplitude

        helper_nodes.append(bm.verts.new([x,y,z]))

    return helper_nodes

    


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
    refined_nodes = insert_helper_nodes(v1, v2, bm)
    for i in range(len(refined_nodes)-1):
        bm.edges.new((refined_nodes[i], refined_nodes[i+1]))
    
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
