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
                render_path,
                render_checkpoint):


        # user defined
        self.plate_size = plate_size
        self.eden_n_iter = eden_n_iter
        self.eden_starter = eden_starter

        self.render_path = render_path
        self.render_checkpoint = render_checkpoint

        # additional variables

        # configure one eden object
        self.eden = EDEN(self.plate_size, 
                    self.eden_n_iter, 
                    self.eden_starter)
        # grow eden object
        self.eden.grow()

        # tubes will be defined with more layers of sca. Every sca layer will contain more sca objects
        layer_1_n_sca = [4,5]
        layer_1_root_center_dist = 7
        layer_1_leaf_cloud_center = [0,0,2]
        layer_1_n_leaves = 10
        layer_1_leaves_spread = [10,10,0]
        layer_1_growth_dist = {'min':1, 'max':5}
        layer_1_eden_layer_center = [0,0,0]
        layer_1_branch_thickenss = 0.7
        self.sca_layer_1 = self.configure_sca_layer(layer_1_n_sca,
                                                    layer_1_root_center_dist,
                                                    layer_1_leaf_cloud_center,
                                                    layer_1_eden_layer_center,
                                                    layer_1_n_leaves,
                                                    layer_1_leaves_spread,
                                                    layer_1_growth_dist,
                                                    layer_1_branch_thickenss)


        layer_2_n_sca = [5,7]
        layer_2_root_center_dist = 20
        layer_2_leaf_cloud_center = [0,0,2]
        layer_2_n_leaves = 20
        layer_2_leaves_spread = [20,20,0]
        layer_2_growth_dist = {'min':2, 'max':8}
        layer_2_eden_layer_center = [0,0,0]
        layer_2_branch_thickenss = 1.2
        self.sca_layer_2 = self.configure_sca_layer(layer_2_n_sca,
                                                    layer_2_root_center_dist,
                                                    layer_2_leaf_cloud_center,
                                                    layer_2_eden_layer_center,
                                                    layer_2_n_leaves,
                                                    layer_2_leaves_spread,
                                                    layer_2_growth_dist,
                                                    layer_2_branch_thickenss)

        # grow all sca objects in sca layer
        for sca in self.sca_layer_1:
            sca.grow()
        
        for sca in self.sca_layer_2:
            sca.grow()

    """ ******************************************************************* 
    PRIVATE FUNCTION
        configures list of sca object that represent sca layer
        lower_upper_n_sca: [min_n_sca, max_n_sca]
        root_center_distance: scalar (distance of root from eden layer center)
        leaf_cloud_center: [xc, yc, zc]
        eden_layer_center: [xc, yc, zc] # zc will be 0
        n_leaves: scalar
        leaves_spread: [xs, ys, zs]
        growth_dist: {'min': min_dist, 'max':max_dist}
    ******************************************************************** """
    def configure_sca_layer(self, 
                            lower_upper_n_sca,
                            root_center_distance,
                            leaf_cloud_center,
                            eden_layer_center,
                            n_leaves,
                            leaves_spread,
                            growth_dist,
                            layer_1_branch_thickenss):

        # list to store sca objects
        sca_layer = []

        # choose random number of SCAs 
        n_sca = np.random.randint(lower_upper_n_sca[0], lower_upper_n_sca[1])

        # generate root centers of every sca on circle around eden layer center
        segment = 2 * math.pi / n_sca
        root_centers = []
        for i in range(n_sca):

            x = eden_layer_center[0] + math.sin(segment * i) * root_center_distance
            y = eden_layer_center[1] + math.cos(segment * i) * root_center_distance
            z = eden_layer_center[2] + 0

            root_centers.append([x,y,z])

        # generate leaf cloud centers 
        leaf_centers = []
        for i in range(n_sca):
            leaf_centers.append(leaf_cloud_center)

        # create objects and store
        for i in range(n_sca):
            sca_layer.append(SCA(root_centers[i],
                                leaf_centers[i],
                                leaves_spread,
                                n_leaves,
                                growth_dist,
                                layer_1_branch_thickenss))

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

        sca_layer_2_metamesh = []
        # add metamesh object for SCA layer 1
        for i in range(len(self.sca_layer_2)):
            sca_meatmesh = bpy.data.metaballs.new("MetaBall")
            sca_metamesh_ref = bpy.data.objects.new("MetaBallObject", sca_meatmesh)
            scene.objects.link(sca_metamesh_ref)
            sca_layer_2_metamesh.append(sca_meatmesh)


        curr_iter = 0

        curr_iter_eden = 0
        eden_iter_block = 10
        eden_rendering_done = False

        curr_iter_sca_l1 = 0
        sca_rendering_cnt_l1 = 0
        sca_rendering_done_l1 = False

        curr_iter_sca_l2 = 0
        sca_rendering_cnt_l2 = 0
        sca_rendering_done_l2 = False 
        
        # display sca leaves for testing purposes
        #for sca in self.sca_layer_1:
        #    self.show_leaves(sca, 0.2)

        # while everything is not displayed
        while True:

            # EDEN MESH ITERATION
            if curr_iter_eden + eden_iter_block < len(self.eden.populated_all):
                self.show_eden_iter(eden_metamesh, 1.5, curr_iter_eden, curr_iter_eden + eden_iter_block)

            elif len(self.eden.populated_all) - curr_iter_eden > 0:
                #flush
                till_end = len(self.eden.populated_all) - curr_iter_eden
                self.show_eden_iter(eden_metamesh, 1.5, curr_iter_eden, curr_iter_eden + till_end-1)

            else:
                eden_rendering_done = True

            curr_iter_eden += eden_iter_block

            if curr_iter_eden >= 100:

                # SCA LAYER 1 MESH ITERATION
                for i in range(len(self.sca_layer_1)):

                    sca = self.sca_layer_1[i]
                    sca_mesh = sca_layer_1_metamesh[i]

                    if curr_iter_sca_l1 < len(sca.branches):
                        self.show_branch(sca, curr_iter_sca_l1, sca_mesh, 1)
                    else:
                        sca_rendering_cnt_l1 += 1

                    if sca_rendering_cnt_l1 >= len(self.sca_layer_1):
                        sca_rendering_done_l1 = True
                        break

                curr_iter_sca_l1 += 1

            if curr_iter_eden >= 500:

                # SCA LAYER 1 MESH ITERATION
                for i in range(len(self.sca_layer_2)):

                    sca = self.sca_layer_2[i]
                    sca_mesh = sca_layer_2_metamesh[i]

                    if curr_iter_sca_l2 < len(sca.branches):
                        self.show_branch(sca, curr_iter_sca_l2, sca_mesh, 1)
                    else:
                        sca_rendering_cnt_l2 += 1

                    if sca_rendering_cnt_l2 >= len(self.sca_layer_2):
                        sca_rendering_done_l2 = True
                        break

                curr_iter_sca_l2 += 1



            # render scene
            if curr_iter % self.render_checkpoint == 0:
                bpy.context.scene.render.filepath = os.path.join(self.render_path, str(curr_iter))
                bpy.ops.render.render(write_still=True)
                
            curr_iter += 1

            if sca_rendering_done_l1 and sca_rendering_done_l2 and eden_rendering_done:
                break
        

    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    Using Blender metamesh display branch between parent and current branch
    ****************************************************************** """
    def show_branch(self, sca, iter, metamesh, n_samples):

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
                element.radius = sca.branch_thickness

                # alternatively add sphere mesh instead of metamesh
                #bpy.ops.mesh.primitive_uv_sphere_add(location=pos, size=0.4, segments=5)

                t += delta_t

    """ *********************************************************************
    PUBLIC HELPER FUNCTION
    Using Blender mesh display leaf position
    ********************************************************************* """
    def show_leaves(self, sca, radius):
        for leaf in sca.leaves:
            bpy.ops.mesh.primitive_cube_add(location=leaf.position, radius=radius)

    """ ****************************************************************************
    PUBLIC HELPER FUNCTION
    using blender mesh display growth for specific iteration
    NOTE: populated_all contains all populated cells in order they were populated
    **************************************************************************** """
    def show_eden_iter(self, metamesh, radius, start_idx, end_idx):

        print(start_idx, end_idx)

        for curr_idx in range(start_idx, end_idx):
            cell = self.eden.populated_all[curr_idx]

            # move metaball in direction of new cell
            element = metamesh.elements.new()
            element.co = self.eden.mapper[(cell[0], cell[1])]
            element.radius = radius



""" ******************************************************************* 
MAIN
******************************************************************** """
def main():

    # create light

    # get scene
    scene = bpy.context.scene

    # create lamp datablock
    lamp_data = bpy.data.lamps.new(name='biolampa', type='POINT')

    # create object with lamp datablock
    lamp_obj = bpy.data.objects.new(name='biolampa', object_data=lamp_data)

    # link lamp object to scene
    scene.objects.link(lamp_obj)

    # cofigure position of lamp
    lamp_obj.location = (10,10,20)
    
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
    render_path = '/home/lovro/Documents/FER/diplomski/Growth_models/blender_implementations/eden_sca/common_out'
    render_checkpoint = 5

    es = eden_sca(plate_size = plate_size,
                eden_n_iter = eden_n_iter,
                eden_starter = eden_starter,
                render_path = render_path,
                render_checkpoint = render_checkpoint)

    es.display_and_render()


""" ******************************************************************* 
ROOT
******************************************************************** """
main()
