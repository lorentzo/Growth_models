import bpy
import numpy as np 
import bmesh
import os

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
    mesh_obj_ps.settings.count = n_points_per_step

    return mesh_obj # can reference data and ps

center = [0, 0, 0]
radius_max = 10
n_steps = 5
radii = np.linspace(0, radius_max, n_steps)
n_points_per_step = 100

points_pet_steps = []

for r_idx in range(len(radii)-1):

    curr_points = []
    r_lower = radii[r_idx]
    r_upper = radii[r_idx + 1]

    for i in range(n_points_per_step):

        found = False
        while not found:

            point = np.random.rand(3) * r_upper

            point[2] = 0

            if np.random.rand() > 0.5:
                point[1] *= -1

            if np.random.rand() > 0.5:
                point[0] *= -1

            if np.linalg.norm(point) < r_upper and np.linalg.norm(point) > r_lower:
                curr_points.append(point)
                found = True

    points_pet_steps.append(curr_points)




# ps object
bpy.ops.mesh.primitive_cube_add()
dupli_cube = bpy.context.object


# add ps to all layers
layers = []
cnt = 1
for points in points_pet_steps:
    layer = define_object(points, "layer"+str(cnt), dupli_cube)
    bpy.context.scene.objects.link(layer)
    layers.append(layer)
    cnt += 1

# render
iter_grow = 10
iter_die = 10
delta_change = 0.01
render_iter = 1
render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/ps_border/tmp/'
for layer in layers:
    print("!")

    for iter in range(iter_grow):
        layer.particle_systems[0].settings.particle_size += delta_change

        # render
        bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
        bpy.ops.render.render(write_still=True)

        render_iter += 1

    for iter in range(iter_die):
        layer.particle_systems[0].settings.particle_size -= delta_change

        # render
        bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
        bpy.ops.render.render(write_still=True)

        render_iter += 1


