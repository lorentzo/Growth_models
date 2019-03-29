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
import math

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
                sca_leaves_spread,
                sca_n_leaves,
                sca_growth_dist,
                render_path,
                render_checkpoint):


        # user defined
        self.plate_size = plate_size
        self.eden_n_iter = eden_n_iter
        self.eden_starter = eden_starter

        self.sca_leaves_spread = sca_leaves_spread
        self.sca_n_leaves = sca_n_leaves
        self.sca_growth_dist = sca_growth_dist

        self.render_path = render_path
        self.render_checkpoint = render_checkpoint

        # additional variables
        self.eden = EDEN(self.plate_size, 
                    self.eden_n_iter, 
                    self.eden_starter)

        self.eden.grow()


        self.sca_layer_1 = self.configure_sca_layer_1([1,4], 10, [0,0,2])

        for sca in self.sca_layer_1:
            sca.grow()

    """ ******************************************************************* 
    PUBLIC FUNCTION
    Layer 1 of SCA
    ******************************************************************** """
    def configure_sca_layer_1(self, upper_lower_n_sca_bound,
                                    root_center_distance,
                                    leaf_cloud_center):

        sca_layer = []

        # choose random number of SCAs 
        n_sca = np.random.randint(upper_lower_n_sca_bound[0], upper_lower_n_sca_bound[1])

        # generate root centers of every sca on circle around eden starter
        segment = 2 * math.pi / n_sca
        root_centers = []
        for i in range(n_sca):
            x = math.sin(segment * i) * root_center_distance
            y = math.cos(segment * i) * root_center_distance
            z = 0
            root_centers.append([x,y,z])

        # generate leaf cloud centers 
        leaf_centers = []
        for i in range(n_sca):
            leaf_centers.append(leaf_cloud_center)

        # create objects and store
        for i in range(n_sca):
            sca_layer.append(SCA(root_centers[i],
                                leaf_centers[i],
                                self.sca_leaves_spread,
                                self.sca_n_leaves,
                                self.sca_growth_dist))

        return sca_layer
            

    """ ******************************************************************* 
    PUBLIC FUNCTION
    call to render
    ******************************************************************** """
    def display_and_render(self):

        # get active scene 
        scene = bpy.context.scene

        # create starter metaball object for EDEN
        eden_metamesh = bpy.data.metaballs.new("MetaBall")
        eden_metamesh_ref = bpy.data.objects.new("MetaBallObject", eden_metamesh)
        scene.objects.link(eden_metamesh_ref)

        sca_layer_1_metamesh = []
        # add metamesh object for SCA layer 1
        for i in range(len(self.sca_layer_1)):
            sca_meatmesh = bpy.data.metaballs.new("MetaBall")
            sca_metamesh_ref = bpy.data.objects.new("MetaBallObject", sca_meatmesh)
            scene.objects.link(sca_metamesh_ref)
            sca_layer_1_metamesh.append(sca_meatmesh)


        curr_iter = 0
        eden_rendering_done = False
        sca_rendering_done = False
        sca_rendering_cnt = 0 
        
        #for sca in self.sca_layer_1:
        #    sca.show_leaves()

        while True:

            # EDEN MESH ITERATION
            if curr_iter < len(self.eden.populated_all):
                self.show_eden_iter(eden_metamesh, curr_iter)
                self.eden.show(eden_metamesh, curr_iter)
                pass
            else:
                eden_rendering_done = True

            # SCA LAYER 1 MESH ITERATION
            for i in range(len(self.sca_layer_1)):

                sca = self.sca_layer_1[i]
                sca_mesh = sca_layer_1_metamesh[i]

                if curr_iter < len(sca.branches):

                    self.show_branch(sca, curr_iter, sca_mesh, 1, 0.5)
                else:
                    sca_rendering_cnt += 1

                if sca_rendering_cnt >= len(self.sca_layer_1):
                    sca_rendering_done = True
                    break

            # render scene
            if curr_iter % self.render_checkpoint == 0:
                bpy.context.scene.render.filepath = os.path.join(self.render_path, str(curr_iter))
                #bpy.ops.render.render(write_still=True)
                
            curr_iter += 1

            if sca_rendering_done and eden_rendering_done:
                break


    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    Using Blender metamesh display branch between parent and current branch
    ****************************************************************** """
    def show_branch(self, sca, iter, metamesh, n_samples, element_radius):

        branch = sca.branches[iter]

        # if distance between parent and current branch is large use interpolation
        delta_t = 1 / n_samples

        if branch.parent != None:

            t = 0
            for sample in range(n_samples):

                # add new metamesh element
                "(1-t) * np.array(branch.parent.position) + t *"
                pos = np.array(branch.position)
                element = metamesh.elements.new()
                element.co = pos
                element.radius = element_radius

                # alternatively add sphere mesh instead of metamesh
                #bpy.ops.mesh.primitive_uv_sphere_add(location=pos, size=0.4, segments=5)

                t += delta_t

    """ ****************************************************************************
    PUBLIC HELPER FUNCTION
    using blender mesh display growth for specific iteration
    NOTE: populated_all contains all populated cells in order they were populated
    **************************************************************************** """
    def show_eden_iter(self, metamesh, iter,):

        cell = self.eden.populated_all[iter]

        # move metaball in direction of new cell
        element = metamesh.elements.new()
        element.co = self.eden.mapper[(cell[0], cell[1])]
        element.radius = 2



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

    # eden sca configuration    
    plate_size = [500,500]
    eden_n_iter = 2200
    eden_starter = [250,250]
    sca_leaves_spread = [10, 10, 0]
    sca_n_leaves = 30
    sca_growth_dist = {'min':0.5, 'max':5}
    render_path = '/home/lovro/Documents/FER/diplomski/Growth_models/blender_implementations/eden_sca/common_out'
    render_checkpoint = 50

    es = eden_sca(plate_size = plate_size,
                eden_n_iter = eden_n_iter,
                eden_starter = eden_starter,
                sca_leaves_spread = sca_leaves_spread,
                sca_n_leaves = sca_n_leaves,
                sca_growth_dist = sca_growth_dist,
                render_path = render_path,
                render_checkpoint = render_checkpoint)

    es.display_and_render()


""" ******************************************************************* 
ROOT
******************************************************************** """
main()
