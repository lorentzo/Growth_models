import bpy
import numpy as np 
import bmesh
import os
from eden_perlin_ps import PerlinCircle

def define_object(points, name, ps_object):

    # create bmesh
    bm = bmesh.new()
    for point in points:
        bm.verts.new(point)
        
    # create mesh from bmesh
    mesh_data = bpy.data.meshes.new(name+"_data")
    mesh_obj = bpy.data.objects.new(name+"_obj", mesh_data)
    bm.to_mesh(mesh_data)
    bm.free()
    
    # add particle system
    mesh_obj.modifiers.new(name+"_ps", type='PARTICLE_SYSTEM')
    mesh_obj_ps = mesh_obj.particle_systems[0]
    mesh_obj_ps.settings.emit_from = 'VERT'
    mesh_obj_ps.settings.particle_size = 0.0
    mesh_obj_ps.settings.render_type = 'OBJECT'
    mesh_obj_ps.settings.dupli_object = ps_object
    mesh_obj_ps.settings.frame_start = 1
    mesh_obj_ps.settings.frame_end = 0
    mesh_obj_ps.settings.use_emit_random = False
    mesh_obj_ps.settings.count = len(points)

    return mesh_obj # can reference data and ps


# define perlin circles
ep = PerlinCircle(center=np.array([0,0,0]), 
                    radius_range=np.array([1, 20, 2]),
                    shape=np.array([1,1]))
    
perlin_layers, perlin_contour = ep.grow()

# ps object
# create texture for displacement
bpy.data.textures.new('diplace_tex', type='VORONOI')
# create sphere
bpy.ops.mesh.primitive_uv_sphere_add(location=[10,10,10], size=1)
# add displacement
bpy.ops.object.modifier_add(type='DISPLACE')
bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["diplace_tex"]
# reference dupli object
dupli_obj = bpy.context.object
dupli_obj.scale = [2,2,0.1]

# add ps to all layers
ps_layers = []
cnt = 1
for points in perlin_contour:
    layer = define_object(points, "layer"+str(cnt), dupli_obj)
    bpy.context.scene.objects.link(layer)
    ps_layers.append(layer)
    cnt += 1

# render
# configure camera position and orientation
bpy.data.objects["Camera"].location = (0, 0, 50)
bpy.data.objects["Camera"].rotation_euler = (0,0,0)

iter_grow = 10
delta_change = 0.02
render_iter = 1
render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/ps_border/tmp/'
for layer_idx in range(len(ps_layers)):

    ps_layer = ps_layers[layer_idx]
    perlin_layer = perlin_layers[layer_idx]

    # add perlin layer
    bpy.context.scene.objects.link(perlin_layer)
    
    # increase ps layer
    for iter in range(iter_grow):

        ps_layer.particle_systems[0].settings.particle_size += delta_change

        # render
        bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
        bpy.ops.render.render(write_still=True)

        render_iter += 1


