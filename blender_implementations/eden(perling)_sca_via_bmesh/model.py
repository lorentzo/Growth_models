import bpy
import bmesh

import numpy as np 
import os

from eden_perlin import PerlinCircle
from sca_brancher import SCACircleBrancher


# get scene
scene = bpy.context.scene

# configure camera position and orientation
bpy.data.objects["Camera"].location = (0, 0, 50)
bpy.data.objects["Camera"].rotation_euler = (0,0,0)

center = np.array([0,0,0])

# eden layer
eden = PerlinCircle(center=center,
                    radius_range=np.array([1,20,2]),
                    shape=np.array([1,1]))

eden_layers = eden.grow()

# sca circle layer
scaCL = SCACircleBrancher(center=center,
                          n_sca_trees=10,
                          root_circle_radius=10,
                          leaves_spread=np.array([10,10,0]),
                          n_leaves=20,
                          name='scaCL')

sca_layers = scaCL.configure_sca_forest()

# render
render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/eden_sca_bmesh/tmp/'
iter = 0
eden_layer_idx = 0

while True:

        iter += 1

        eden_layer = eden_layers[eden_layer_idx]

        # add object to scene in
        scene.objects.link(eden_layer)  

        if eden_layer_idx == 5:
            for sca_layer in sca_layers:
                scene.objects.link(sca_layer)

        # render
        bpy.context.scene.render.filepath = os.path.join(render_out, str(iter))
        bpy.ops.render.render(write_still=True)

        eden_layer_idx += 1


    
