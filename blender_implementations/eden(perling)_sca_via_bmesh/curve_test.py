import bpy
import numpy as np
import bmesh
from mathutils import noise

# create empty bmesh to store vertices of circle
bm = bmesh.new()

# divide circle in segments
circle_segments = np.linspace(0, 2*np.pi, 50)

for segment in circle_segments:

        # generate point on a cricle as argument to perlin noise
        xoff = np.interp(np.cos(segment), [-1,1], [0.1,0.9])
        yoff = np.interp(np.sin(segment), [-1,1], [0.1,0.9])
        zoff = 4.12

        pos = np.array([xoff, yoff, zoff])

        # generate noise value
        noise_val = noise.noise(pos) # NB: noise elem [-1,1]

        # add to radius
        radius_curr_x = 10 + noise_val
        radius_curr_y = 10 + noise_val

        # create circle point on nosy radius from center
        x = 0 + radius_curr_x * np.cos(segment)
        y = 0 + radius_curr_y * np.sin(segment)
        z = 0

        # add  point to bmesh
        bm.verts.new(np.array([x,y,z]))
        
bm.faces.new(bm.verts)
"""
# add randomised vertices
for i in range(100):
    
    #for i in np.linspace(-20, 20, 10):
        #for j in np.linspace(-20,20,10):
            if np.linalg.norm(np.array([i,j])) < 10:
                
                k = np.interp(noise.noise(np.array([i,j,np.pi])), [-1,1], [0,2])
                bm.verts.new(np.array([i,j,k]))

bm.faces.new(bm.verts)
"""


# add a new mesh data
layer_mesh_data = bpy.data.meshes.new("data")  

# add a new empty mesh object using the mesh data
layer_mesh_object = bpy.data.objects.new("object", layer_mesh_data) 

# make the bmesh the object's mesh
# transfer bmesh data do mesh data which is connected to empty mesh object
bm.to_mesh(layer_mesh_data)

bm.free()

scene = bpy.context.scene
scene.objects.link(layer_mesh_object) 