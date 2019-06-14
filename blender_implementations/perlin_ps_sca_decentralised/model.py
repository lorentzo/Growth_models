# -*- coding: utf-8 -*-
""" Main file.

This file constructs the Perlin border model with particle system
and SCA layers.
When all models are constructed it creates Blender objects and 
performs the rendering.

"""

# Project specific imports.
from sca_brancher import SCACircleBrancher
from perlin_ps_border import PerlinPSBorder

# Blender imports.
import bpy

# Standard imports.
import numpy as np
import os
from colorsys import hsv_to_rgb

# Get scene.
scene = bpy.context.scene

# Get and configure camera.
bpy.data.objects["Camera"].location = (0, 0, 50)
bpy.data.objects["Camera"].rotation_euler = (0,0,0)

# Get and configure light.
bpy.data.objects["Lamp"].data.type = 'SUN'

# Configure and grow the Perlin border model.
perlin_ps = PerlinPSBorder(center=[0,0,0],
                                  radius_range=[0.01,16,32],
                                  color_perlin_border=hsv_to_rgb(30.0/360.0, 80.0/100.0, 80.0/100.0),
                                  color_ps=hsv_to_rgb(30.0/360.0, 80.0/100.0, 80.0/100.0))

perlin_layers, ps_layers, radii = perlin_ps.give_perlin_ps()

# Container for SCA layers.
sca_layers = {}

# SCA circle layer 1.
scaCL1_radius = 2
scaCL1 = SCACircleBrancher(center=[0,0,0.03],
                          n_sca_trees=10,
                          root_circle_radius=scaCL1_radius,
                          leaf_center_radius=scaCL1_radius-1.5,
                          leaves_spread=np.array([3,3,1]),
                          n_leaves=10,
                          branch_thickness_max=0.1,
                          bevel_radius_delta = 0.0012,
                          name='scaCLA',
                          color=hsv_to_rgb(30.0/360.0,50.0/100.0,50.0/100.0))

scaCL1.initialize_sca_forest(scene)
sca_layers[scaCL1_radius] = scaCL1

# SCA layer 2.
scaCL2_radius = 5
scaCL2 = SCACircleBrancher(center=[0,0,0.03],
                          n_sca_trees=15,
                          root_circle_radius=scaCL2_radius,
                          leaf_center_radius= scaCL2_radius - 3,
                          leaves_spread=np.array([5,5,1]),
                          n_leaves=15,
                          branch_thickness_max=0.1,
                          bevel_radius_delta=0.0015,
                          name='scaCLB',
                          color=hsv_to_rgb(30.0/360.0,50.0/100.0,70.0/100.0))

scaCL2.initialize_sca_forest(scene)
sca_layers[scaCL2_radius] = scaCL2

# SCA circle layer 3.
scaCL3_radius = 9
scaCL3 = SCACircleBrancher(center=[0,0,0.03],
                          n_sca_trees=20,
                          root_circle_radius=scaCL3_radius,
                          leaf_center_radius=scaCL3_radius - 6,
                          leaves_spread=np.array([8,8,1]),
                          n_leaves=20,
                          branch_thickness_max=0.12,
                          bevel_radius_delta=0.003,
                          name='scaCLC',
                          color=hsv_to_rgb(30.0/360.0,50.0/100.0,60.0/100.0))

scaCL3.initialize_sca_forest(scene)
sca_layers[scaCL3_radius] = scaCL3

# SCA circle layer 4.
scaCL4_radius = 13
scaCL4 = SCACircleBrancher(center=[0,0,0.03],
                          n_sca_trees=25,
                          root_circle_radius=scaCL4_radius,
                          leaf_center_radius=scaCL4_radius - 10,
                          leaves_spread=np.array([15,15,1]),
                          n_leaves=25,
                          branch_thickness_max=0.17,
                          bevel_radius_delta=0.005,
                          name='scaCLD',
                          color=hsv_to_rgb(30.0/360.0,50.0/100.0,50.0/100.0))

scaCL4.initialize_sca_forest(scene)
sca_layers[scaCL4_radius] = scaCL4


# Rendering.
render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/perlin_ps_sca/tmp/'
render_iter = 0

n_perlin_layer = 0
perlin_layers_done = False

n_ps_layer = 0
ps_layers_done = False

sca_layers_done = False

while True:

    # Render the itration of Perlin border model.
    if n_perlin_layer < len(perlin_layers):
        scene.objects.link(perlin_layers[n_perlin_layer])
    else:
        perlin_layers_done = True

    #bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
    #bpy.ops.render.render(write_still=True)
    #render_iter += 1

    # Render the iteration of PS layer 
    if n_ps_layer < len(ps_layers):

        ps_layer = ps_layers[n_ps_layer]

        for i in range(5):
            
            ps_layer.particle_systems[0].settings.particle_size += 0.04

            for sca_radius, sca_layer in sca_layers.items():
                if radii[n_perlin_layer] > sca_radius:
                    sca_layer.emerge_sca_volume()

            #bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
            #bpy.ops.render.render(write_still=True)
            #render_iter += 1
    else:
        ps_layers_done = True


    # Render SCA iteration.
    sca_layers_rendered = 0
    for sca_radius, sca_layer in sca_layers.items():
        if n_perlin_layer >= len(perlin_layers):
            n_perlin_layer = len(perlin_layers) - 1
        if radii[n_perlin_layer] > sca_radius:
            if sca_layer.emerge_sca_volume():
                sca_layers_rendered += 1

    if sca_layers_rendered == len(sca_layers):
        sca_layers_done = True

    #bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
    #bpy.ops.render.render(write_still=True)
    #render_iter += 1

    if perlin_layers_done and ps_layers_done and sca_layers_done:
        break

    n_perlin_layer += 1
    n_ps_layer += 1