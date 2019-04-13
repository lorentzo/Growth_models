from mathutils import noise
import numpy as np 
import bpy
import bmesh

def perlin_circle(bm, param):
    
    circle_segments = np.linspace(0, 2*np.pi, param["n_segments"])

    for segment in circle_segments:
        
        xoff = np.interp(np.cos(segment), [-1,1], param["xoff"])
        yoff = np.interp(np.sin(segment), [-1,1], param["yoff"])
        zoff = param["zoff"]

        pos = np.array([xoff, yoff, zoff])
        
        # ZANIMLJIVO: ako ne koristis mapiranje na [50,100] dobivas latice!
        radius = noise.noise(pos) * (param["radius"][1] - param["radius"][0]+1) + param["radius"][0]
        #radius = np.interp(noise.noise(pos), [0,1], param["radius"])
        
        x = radius * np.cos(segment)
        y = radius * np.sin(segment)

        bm.verts.new(np.array([x,y,0]))


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
            {"n_segments":200, "xoff":[0,0.3], "yoff":[0,0.3], "zoff":13.2, "radius":[1,3], "step":1},
            {"n_segments":200, "xoff":[0,2], "yoff":[0,2], "zoff":14.3, "radius":[3,7], "step":2},
            {"n_segments":200, "xoff":[0,4.1], "yoff":[0,4.1], "zoff":10.2, "radius":[7,10], "step":3},
            {"n_segments":200, "xoff":[0,7], "yoff":[0,7], "zoff":18.2, "radius":[10,13], "step":4},
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