from mathutils import noise
import numpy as np 
import bpy

segment = np.pi + 0.1
xoff = np.interp(np.cos(segment), [-1,1], [2,7])
yoff = np.interp(np.sin(segment), [-1,1], [2,7])
zoff = 0.4

pos = np.array([xoff, yoff, zoff])

val = noise.noise(pos)
radius = np.interp(val, [0,1], [2,7])

print(xoff, yoff, zoff)
print(val, radius)

"""
from mathutils import noise
import numpy as np 
import bpy
import bmesh

class PerlinCircle:
    
    def __init

def perlin_circle(bm, param):
    
    circle_segments = np.linspace(0, 2*np.pi, param["n_segments"])
    center = np.array([-1,-1,0])
    radius = 2

    for segment in circle_segments:
        
        # generate point on a cricle as argument to perlin noise
        xoff = np.interp(np.cos(segment), [-1,1], param["xnoise"])
        yoff = np.interp(np.sin(segment), [-1,1], param["ynoise"])
        zoff = param["zoff"]

        pos = np.array([xoff, yoff, zoff])

        # generate noise value
        noise_val = noise.noise(pos) # NB: noise elem [-1,1]
        
        # add to radius
        radius_curr = radius + noise_val
        
        # create circle point on nosy radius from center
        x = center[0] + radius_curr * np.cos(segment)
        y = center[1] + radius_curr * np.sin(segment)
        z = center[2]

        # add  point to bmesh
        bm.verts.new(np.array([x,y,z]))


def grow(layer_name, params):

    scene = bpy.context.scene

    # get layer object mesh
    eden_layer_mesh_object = bpy.data.objects[layer_name]

    # get layer data mesh
    eden_layer_mesh_data = eden_layer_mesh_object.data

    # loop with different perlin circle parameters
    for param in params:

        # create new bmesh
        bm = bmesh.new()

        # add vertices to bm mesh according to perlin circle vertices generation
        perlin_circle(bm, param)

        # make the bmesh the object's mesh
        # transfer bmesh data do mesh data which is connected to empty mesh object
        bm.to_mesh(eden_layer_mesh_data)

        # add faces/edges
        # make mesh object active
        
        scene.objects.active = eden_layer_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.mode_set(mode='OBJECT')

        # render
        bpy.context.scene.render.filepath = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/eden_perlin/tmp/' + str(param["step"])
        bpy.ops.render.render(write_still=True)

        # free when finished
        bm.free()

def generate_params():

    params = [
            {"n_segments":200, "xnoise":[0,5], "ynoise":[0,5], "zoff":13.2, "radius":[0,5], "step":1},
            {"n_segments":200, "xnoise":[0,5], "ynoise":[0,5], "zoff":14.3, "radius":[3,7], "step":2},
            {"n_segments":200, "xnoise":[0,5], "ynoise":[0,5], "zoff":10.2, "radius":[7,10], "step":3},
            {"n_segments":200, "xnoise":[0,7], "ynoise":[0,7], "zoff":18.2, "radius":[10,13], "step":4},
             ]

    return params

def main():    

    # get scene
    scene = bpy.context.scene

    # configure camera position and orientation
    bpy.data.objects["Camera"].location = (0, 0, 50)
    bpy.data.objects["Camera"].rotation_euler = (0,0,0)

    "prepare mesh data and mesh object that will be used as eden layer"

    # add a new mesh data
    eden_layer_data = bpy.data.meshes.new("eden_layer_A_data")  

    # add a new empty mesh object using the mesh data
    eden_layer_object = bpy.data.objects.new("eden_layer_A_object", eden_layer_data)  

    # put the empty mesh object into the scene (link)
    scene.objects.link(eden_layer_object)  


    "perform growth"
    params = generate_params()
    grow("eden_layer_A_object", params)


   
main()


"""
        # ZANIMLJIVO: ako ne koristis mapiranje za noise dobivas latice!
"""
"""