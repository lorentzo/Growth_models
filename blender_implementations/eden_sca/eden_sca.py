#############################################################################
# DESCRIPTION:
# biofilm spreading based on Eden's growth model and SCA model
#############################################################################
""" ******************************************************************* 
IMPORTS
******************************************************************** """
########################## STANDARD LIBRARIES ##########################
import bpy
import numpy as np
import os

########################## USER LIBRARIES ##############################
from eden import EDEN
from sca import SCA

""" ******************************************************************* 
CLASS
Defining EDEN and SCA model
******************************************************************** """
class eden_sca:

    """ ******************************************************************* 
    CONSTRUCTOR
    ******************************************************************** """
    def __init__(self, 
                plate_size,
                eden_n_iter,
                eden_starter,
                sca_n_leaves,
                sca_root_position,
                sca_max_dist,
                sca_min_dist,
                sca_xy_leaves_spread,
                sca_z_leaves_spread,
                render_path,
                render_checkpoint):


        # user defined
        self.plate_size = plate_size
        self.eden_n_iter = eden_n_iter
        self.eden_starter = eden_starter
        self.sca_n_leaves = sca_n_leaves
        self.sca_root_position = sca_root_position
        self.sca_max_dist = sca_max_dist
        self.sca_min_dist = sca_min_dist
        self.sca_xy_leaves_spread = sca_xy_leaves_spread
        self.sca_z_leaves_spread = sca_z_leaves_spread
        self.render_path = render_path
        self.render_checkpoint = render_checkpoint

        # additional variables
        self.eden = None
        self.sca = None
        

    """ ******************************************************************* 
    PUBLIC FUNCTION
    call to grow
    ******************************************************************** """
    def grow(self):

        render_path = '/home/lovro/Documents/FER/diplomski/Growth_models/blender_implementations/eden_sca/eden_out'

        # configure eden
        self.eden = EDEN(self.plate_size, 
                    self.eden_n_iter, 
                    self.eden_starter)

        # configure sca
        self.sca = SCA(self.sca_n_leaves, 
                  self.sca_root_position, 
                  self.sca_max_dist,
                  self.sca_min_dist,
                  self.sca_xy_leaves_spread,
                  self.sca_z_leaves_spread)

        # grow eden and take locations
        self.eden.grow()

        # grow sca and take leaves and branches branches
        self.sca.grow()

    """ ******************************************************************* 
    PUBLIC FUNCTION
    call to render
    ******************************************************************** """
    def render(self):

        # get active scene 
        scene = bpy.context.scene

        # create starter metaball object for EDEN
        eden_metamesh = bpy.data.metaballs.new("MetaBall")
        eden_metamesh_ref = bpy.data.objects.new("MetaBallObject", eden_metamesh)
        scene.objects.link(eden_metamesh_ref)

        # add metamesh object for SCA
        sca_meatmesh = bpy.data.metaballs.new("MetaBall")
        sca_metamesh_ref = bpy.data.objects.new("MetaBallObject", sca_meatmesh)
        scene.objects.link(sca_metamesh_ref)

        curr_iter = 0
        eden_rendering_done = False
        sca_rendering_done = False
        
        self.sca.show_leaves()

        while True:

            # EDEN MESH ITERATION
            if curr_iter < len(self.eden.populated_all):
                self.eden.show(eden_metamesh, curr_iter)
            else:
                eden_rendering_done = True

            # SCA MESH ITERATION
            if curr_iter < len(self.sca.branches):
                self.sca.show_branches(sca_meatmesh, curr_iter)
            else:
                sca_rendering_done = True

            # render scene
            if curr_iter % self.render_checkpoint == 0:
                bpy.context.scene.render.filepath = os.path.join(self.render_path, str(curr_iter))
                bpy.ops.render.render(write_still=True)
                
            curr_iter += 1

            if sca_rendering_done and eden_rendering_done:
                break

""" ******************************************************************* 
MAIN
******************************************************************** """
def main():
    
    # configure camera position and orientation
    bpy.data.objects["Camera"].location[0] = 0
    bpy.data.objects["Camera"].location[1] = 0
    bpy.data.objects["Camera"].location[2] = 100
    bpy.data.objects["Camera"].rotation_euler[0] = 0
    bpy.data.objects["Camera"].rotation_euler[1] = 0
    bpy.data.objects["Camera"].rotation_euler[2] = 0

    # render path
    render_path = '/home/lovro/Documents/FER/diplomski/Growth_models/blender_implementations/eden_sca/common_out'

    es = eden_sca([500,500], 1000, [250,250],
                  100, [10,10,10], 1, 0.1, 20, 4,
                  render_path, 50)

    es.grow()
    es.render()



""" ******************************************************************* 
ROOT
******************************************************************** """
main()
