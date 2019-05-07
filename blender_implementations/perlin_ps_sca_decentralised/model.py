from ps_border import EDEN_PERLIN_PS_BORDER
from sca_brancher import SCACircleBrancher

import numpy as np
import os
from colorsys import hsv_to_rgb

import bpy

# get scene
scene = bpy.context.scene
bpy.data.objects["Camera"].location = (0, 0, 50)
bpy.data.objects["Camera"].rotation_euler = (0,0,0)

# perlin(eden) and ps layers
perlin_ps = EDEN_PERLIN_PS_BORDER(center=[0,0,0],
                                  radius_range=[0.01,16,20])

perlin_layers, ps_layers, radii = perlin_ps.give_perlin_ps()

# sca layers
sca_layers = {}

# sca circle layer 1
scaCL1_radius = 3
scaCL1 = SCACircleBrancher(center=[0,0,0.3],
                          n_sca_trees=10,
                          root_circle_radius=scaCL1_radius,
                          leaf_center_radius=scaCL1_radius-1,
                          leaves_spread=np.array([3,3,1]),
                          n_leaves=10,
                          branch_thickness_max=0.1,
                          name='scaCLA',
                          color=hsv_to_rgb(15/360.0,27/100.0,80/100.0))

scaCL1.initialize_sca_forest(scene)
sca_layers[scaCL1_radius] = scaCL1

# sca layer 2
scaCL2_radius = 6
scaCL2 = SCACircleBrancher(center=[0,0,0.3],
                          n_sca_trees=15,
                          root_circle_radius=scaCL2_radius,
                          leaf_center_radius= scaCL2_radius - 4,
                          leaves_spread=np.array([5,5,1]),
                          n_leaves=15,
                          branch_thickness_max=0.1,
                          name='scaCLB',
                          color=hsv_to_rgb(15/360.0,27/100.0,70/100.0))

scaCL2.initialize_sca_forest(scene)
sca_layers[scaCL2_radius] = scaCL2

# sca circle layer 3
scaCL3_radius = 10
scaCL3 = SCACircleBrancher(center=[0,0,0.3],
                          n_sca_trees=20,
                          root_circle_radius=scaCL3_radius,
                          leaf_center_radius=scaCL3_radius - 7,
                          leaves_spread=np.array([8,8,1]),
                          n_leaves=20,
                          branch_thickness_max=0.15,
                          name='scaCLC',
                          color=hsv_to_rgb(15/360.0,27/100.0,60/100.0))

scaCL3.initialize_sca_forest(scene)
sca_layers[scaCL3_radius] = scaCL3

# sca circle layer 4
scaCL4_radius = 15
scaCL4 = SCACircleBrancher(center=[0,0,0.2],
                          n_sca_trees=25,
                          root_circle_radius=scaCL4_radius,
                          leaf_center_radius=scaCL4_radius - 10,
                          leaves_spread=np.array([15,15,1]),
                          n_leaves=25,
                          branch_thickness_max=0.20,
                          name='scaCLD',
                          color=hsv_to_rgb(15/360.0,27/100.0,50/100.0))

scaCL4.initialize_sca_forest(scene)
sca_layers[scaCL4_radius] = scaCL4


# render
render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/perlin_ps_sca/tmp/'
render_iter = 0

n_perlin_layer = 0
perlin_layers_done = False

n_ps_layer = 0
ps_layers_done = False

sca_layers_done = False

while True:

    # render perlin
    if n_perlin_layer < len(perlin_layers):
        scene.objects.link(perlin_layers[n_perlin_layer])
    else:
        perlin_layers_done = True

    bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
    bpy.ops.render.render(write_still=True)
    render_iter += 1

    # render ps
    if n_ps_layer < len(ps_layers):
        ps_layer = ps_layers[n_ps_layer]
        for i in range(10):
            ps_layer.particle_systems[0].settings.particle_size += 0.02

            bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
            bpy.ops.render.render(write_still=True)
            render_iter += 1
    else:
        ps_layers_done = True


    # render sca
    sca_layers_rendered = 0
    for sca_radius, sca_layer in sca_layers.items():
        if radii[n_perlin_layer] > sca_radius:
            if sca_layer.emerge_sca_volume():
                sca_layers_rendered += 1

    if sca_layers_rendered == len(sca_layers):
        sca_layers_done = True

    bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
    bpy.ops.render.render(write_still=True)
    render_iter += 1

    if perlin_layers_done and ps_layers_done and sca_layers_done:
        break

    n_perlin_layer += 1
    n_ps_layer += 1


    