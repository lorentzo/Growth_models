import bpy
import numpy as np
import bmesh
from sca import SCA

def create_circle(pos, r):

    err = 0.005
    print("*********", r)
    th = np.arccos(2 * np.power((1 - err / r), 2) - 1)
    print("*********************",th)
    n = np.ceil(2 * np.pi / th)
    phis = np.linspace(0, 2*np.pi, n)

    bm = bmesh.new()

    for phi in phis:

        x = pos[0] + r * np.cos(phi)
        y = pos[1] + r * np.sin(phi)

        bm.verts.new([x,y,0])

    bm.faces.new(bm.verts)

    # add a new mesh data
    layer_mesh_data = bpy.data.meshes.new("data")  

    # add a new empty mesh object using the mesh data
    layer_mesh_object = bpy.data.objects.new("object", layer_mesh_data) 

    # make the bmesh the object's mesh
    # transfer bmesh data do mesh data which is connected to empty mesh object
    bm.to_mesh(layer_mesh_data)
    bm.free()

    bpy.context.scene.objects.link(layer_mesh_object)






sca = SCA(root_position=[0,0,0],
          leaves_cloud_center=[0,0,0],
          leaves_spread=[15,15,0],
          n_leaves=100,
          growth_dist={"min":0.5,"max":4})

sca.grow()

bm = bmesh.new()

max_r = 1

for branch in sca.branches:
    if branch.parent == None:
        continue
    v1 = bm.verts.new(branch.position)
    v2 = bm.verts.new(branch.parent.position)
    bm.edges.new((v1, v2))

    r_curr = np.linalg.norm(v2.co)
    r = np.interp(r_curr, [0, 15], [max_r, 1e-2])
    create_circle(v2.co, r)

    r_curr = np.linalg.norm(v1.co)
    r = np.interp(r_curr, [0, 15], [max_r, 1e-2])
    create_circle(v1.co, r)



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
