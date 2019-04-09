from mathutils import noise
import numpy as np 
import bpy
import bmesh

def perlin_circle(bm):
    
    n_segments = 200
    
    xoff_lower = 0
    xoff_upper = 3.4
    
    yoff_lower = 0
    yoff_upper = 3.2
    zoff = 13.2
    z = 1
    
    radius_lower = 10
    radius_upper = 12
    
    circle_segments = np.linspace(0, 2*np.pi, n_segments)
    
    curr_iter  = 0

    for segment in circle_segments:
        
        print("segment", segment)

        xoff = (np.cos(segment)+1) * (xoff_upper + 1 - xoff_lower) + xoff_lower
        yoff = (np.sin(segment)+1) * (yoff_upper + 1 - yoff_lower) + yoff_lower

        pos = np.array([xoff, yoff, zoff])
        print("perlin argument:", pos)
        
        # ZANIMLJIVO: ako ne koristis mapiranje na [50,100] dobivas latice!
        radius = noise.noise(pos) * (radius_upper - radius_lower+1) + radius_lower
        print("perlin vrijednost", radius)
        
        x = radius * np.cos(segment)
        y = radius * np.sin(segment)

        bm.verts.new(np.array([x,y,0]))

        """
        #bpy.ops.mesh.primitive_cube_add(radius=0.5, location=(x,y,z))
        element = meatmesh_datablock.elements.new(type='BALL')
        element.co = (x,y,z)
        element.radius = 1
        """
        
        if curr_iter % 10 == 0:
            bpy.context.scene.render.filepath = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/eden_perlin/' + str(curr_iter)
            #bpy.ops.render.render(write_still=True)
            
        curr_iter += 1



def main():    

    # configure camera position and orientation
    bpy.data.objects["Camera"].location = (0, 0, 100)
    bpy.data.objects["Camera"].rotation_euler = (0,0,0)

    # get scene
    scene = bpy.context.scene

    """
    "METAMESH"
    # create datablock
    meatmesh_datablock = bpy.data.metaballs.new("data_block_name")
    # create object
    metamesh_obj = bpy.data.objects.new("object_name", meatmesh_datablock)
    # add material
    material = bpy.data.materials.new(name="Material_"+"data_block_name")
    metamesh_obj.active_material = material
    # add color
    metamesh_obj.active_material.diffuse_color = (0.2,0.3,0.4)
    # link to scene
    scene.objects.link(metamesh_obj)
    """


    "BMESH"
    # add a new mesh data
    eden_layer_data = bpy.data.meshes.new("mesh")  
    # add a new object using the mesh data
    eden_layer_object = bpy.data.objects.new("MyObject", eden_layer_data)  

    # put the object into the scene (link)
    scene.objects.link(eden_layer_object)  
    # set as the active object in the scene
    scene.objects.active = eden_layer_object 
    # select object
    eden_layer_object.select = True 

    # select mesh data
    mesh = bpy.context.object.data

    # create bmesh for adding the vertices
    bm = bmesh.new()

    perlin_circle(bm)

    # make the bmesh the object's mesh
    bm.to_mesh(eden_layer_data)

    # add faces/edges
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode='OBJECT')

    # free when finished
    bm.free()


main()