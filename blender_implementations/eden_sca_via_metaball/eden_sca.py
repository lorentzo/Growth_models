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
                eden2_n_iter,
                eden_starter,
                render_path,
                render_checkpoint):


        # user defined variables
        self.plate_size = plate_size
        self.eden_n_iter = eden_n_iter
        self.eden2_n_iter = eden2_n_iter
        self.eden_starter = eden_starter

        self.render_path = render_path
        self.render_checkpoint = render_checkpoint

        # configure one eden object
        self.eden = EDEN(self.plate_size, 
                    self.eden_n_iter, 
                    self.eden_starter)
        # grow eden object
        self.eden.grow()

        # configure another eden object, this one is smaller and on a top of previous
        self.eden2 = EDEN(self.plate_size, 
                    self.eden2_n_iter, 
                    self.eden_starter)
        # grow eden object
        self.eden2.grow()

        # tubes will be defined with more layers of sca. Every sca layer will contain more sca objects
        self.sca_layer_1 = self.configure_sca_layer(lower_upper_n_sca=[5,7],
                                                    root_center_distance=7,
                                                    leaf_cloud_center=[0,0,2],
                                                    eden_layer_center=[0,0,0],
                                                    n_leaves=10,
                                                    leaves_spread=[10,10,0],
                                                    growth_dist={'min':1, 'max':5},
                                                    branch_thickenss=0.9)

        self.sca_layer_2 = self.configure_sca_layer(lower_upper_n_sca=[8,10],
                                                    root_center_distance=14,
                                                    leaf_cloud_center=[0,0,2],
                                                    eden_layer_center=[0,0,0],
                                                    n_leaves=20,
                                                    leaves_spread=[20,20,0],
                                                    growth_dist={'min':2, 'max':8},
                                                    branch_thickenss=1.1)

        self.sca_layer_3 = self.configure_sca_layer(lower_upper_n_sca=[9,12],
                                                    root_center_distance=23,
                                                    leaf_cloud_center=[0,0,2],
                                                    eden_layer_center=[0,0,0],
                                                    n_leaves=15,
                                                    leaves_spread=[30,30,0],
                                                    growth_dist={'min':2, 'max':8},
                                                    branch_thickenss=1.2)

        # grow all sca objects in sca layer
        for sca in self.sca_layer_1:
            sca.grow()
        
        for sca in self.sca_layer_2:
            sca.grow()

        for sca in self.sca_layer_3:
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
                            branch_thickenss):

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
                                branch_thickenss))

        return sca_layer
            

    """ ******************************************************************* 
    PUBLIC FUNCTION
    call to render
    ******************************************************************** """
    def display_and_render(self):

        # get active scene 
        scene = bpy.context.scene

        # create starter metaball object for EDEN
        eden_metamesh_datablock = self.create_metamesh_object(n_objects=1,
                                                              scene=scene,
                                                              data_block_name="MetaEden",
                                                              object_name="MetaEden",
                                                              rgb=(0.47, 0.35, 0.18))

        # eden rendering info
        curr_iter_eden = 0
        eden_iter_block = 10
        eden_rendering_done = False

        # create starter metaball object for EDEN
        eden_metamesh_datablock2 = self.create_metamesh_object(n_objects=1,
                                                              scene=scene,
                                                              data_block_name="MetaEdenB",
                                                              object_name="MetaEdenB",
                                                              rgb=(0.40, 0.25, 0.1))

        # eden rendering info
        curr_iter_eden2 = 0
        eden_iter_block2 = 5
        eden_rendering_done2 = False

        # create metaball for sca 1
        sca_layer_1_metamesh = self.create_metamesh_object(n_objects=len(self.sca_layer_1),
                                                                scene=scene,
                                                                data_block_name="MetaSCAB",
                                                                object_name="MetaSCAB",
                                                                rgb=(0.53, 0.36, 0.12))

        # rendering info for sca 1
        curr_iter_sca_l1 = 0
        sca_rendering_cnt_l1 = 0
        sca_rendering_done_l1 = False

        # create metaball for sca 2
        sca_layer_2_metamesh = self.create_metamesh_object(n_objects=len(self.sca_layer_2),
                                                                scene=scene,
                                                                data_block_name="MetaSCAC",
                                                                object_name="MetaSCAC",
                                                                rgb=(0.56, 0.37, 0.07))

        # rendering info for sca 2
        curr_iter_sca_l2 = 0
        sca_rendering_cnt_l2 = 0
        sca_rendering_done_l2 = False 

        # create metaball for sca 3
        sca_layer_3_metamesh = self.create_metamesh_object(n_objects=len(self.sca_layer_3),
                                                                scene=scene,
                                                                data_block_name="MetaSCAD",
                                                                object_name="MetaSCAD",
                                                                 rgb=(0.57, 0.37, 0.06))

        # rendering info for sca 3
        curr_iter_sca_l3 = 0
        sca_rendering_cnt_l3 = 0
        sca_rendering_done_l3 = False 

        # overall iteration
        curr_iter = 0

        # display sca leaves for testing purposes
        #for sca in self.sca_layer_1:
        #    self.show_leaves(sca, 0.2)

        # while everything is not displayed
        while True:

            curr_iter_eden, eden_rendering_done = self.eden_iter(eden_layer=self.eden,
                                                                eden_metamesh_datablock=eden_metamesh_datablock,
                                                                curr_iter_eden=curr_iter_eden,
                                                                eden_iter_block=eden_iter_block,
                                                                eden_rendering_done=eden_rendering_done)

            if curr_iter_eden > 350:
                curr_iter_eden2, eden_rendering_done2 = self.eden_iter(eden_layer=self.eden2,
                                                                    eden_metamesh_datablock=eden_metamesh_datablock2,
                                                                    curr_iter_eden=curr_iter_eden2,
                                                                    eden_iter_block=eden_iter_block2,
                                                                    eden_rendering_done=eden_rendering_done2,
                                                                    height=0.5)

            # display sca layer 1
            if curr_iter_eden >= 400:

                curr_iter_sca_l1, sca_rendering_cnt_l1, sca_rendering_done_l1 = self.sca_iter(self.sca_layer_1, 
                                                                                            sca_layer_1_metamesh, 
                                                                                            curr_iter_sca_l1, 
                                                                                            sca_rendering_cnt_l1, 
                                                                                            sca_rendering_done_l1)
            # display sca layer 2
            if curr_iter_eden >= 700:

                curr_iter_sca_l2, sca_rendering_cnt_l2, sca_rendering_done_l2 = self.sca_iter(self.sca_layer_2, 
                                                                                            sca_layer_2_metamesh, 
                                                                                            curr_iter_sca_l2, 
                                                                                            sca_rendering_cnt_l2, 
                                                                                            sca_rendering_done_l2)
    
            # display sca layer 3
            if curr_iter_eden >= 1300:

                curr_iter_sca_l3, sca_rendering_cnt_l3, sca_rendering_done_l3 = self.sca_iter(self.sca_layer_3, 
                                                                                            sca_layer_3_metamesh, 
                                                                                            curr_iter_sca_l3, 
                                                                                            sca_rendering_cnt_l3, 
                                                                                            sca_rendering_done_l3)

            # render scene
            if curr_iter % self.render_checkpoint == 0:
                bpy.context.scene.render.filepath = os.path.join(self.render_path, str(curr_iter))
                bpy.ops.render.render(write_still=True)
                
            curr_iter += 1

            # if all displayed and rendered: exit
            if sca_rendering_done_l1 and sca_rendering_done_l2 and sca_rendering_done_l3 and eden_rendering_done and eden_rendering_done2:
                break

    """ ******************************************************************
    PRIVATE HELPER FUNCTION
    Create meta mesh objectsf for sca layer
    ****************************************************************** """
    def create_metamesh_object(self, n_objects, scene, data_block_name, object_name, rgb):

        metamesh = []

        for i in range(n_objects):

            # create datablock
            meatmesh_datablock = bpy.data.metaballs.new(data_block_name)

            # create object
            metamesh_obj = bpy.data.objects.new(object_name, meatmesh_datablock)

            # add material
            material = bpy.data.materials.new(name="Material_"+data_block_name)
            metamesh_obj.active_material = material

            # add color
            metamesh_obj.active_material.diffuse_color = rgb

            # link to scene
            scene.objects.link(metamesh_obj)

            metamesh.append(meatmesh_datablock)

        if n_objects == 1:
            return metamesh[0]
        
        else:
            return metamesh

    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    For specific eden layer, display one iteration of growth 
    ****************************************************************** """
    def eden_iter(self,
                  eden_layer,
                  eden_metamesh_datablock,
                  curr_iter_eden,
                  eden_iter_block,
                  eden_rendering_done,
                  height=0
                  ):

        # EDEN MESH ITERATION
        if curr_iter_eden + eden_iter_block < len(eden_layer.populated_all):
            self.show_eden_iter(eden_metamesh_datablock, 
                                1.5, 
                                curr_iter_eden, 
                                curr_iter_eden + eden_iter_block,
                                height)

        elif len(eden_layer.populated_all) - curr_iter_eden > 0:
            # flush the last iterations
            till_end = len(eden_layer.populated_all) - curr_iter_eden
            self.show_eden_iter(eden_metamesh_datablock, 
                                1.5, 
                                curr_iter_eden, 
                                curr_iter_eden + till_end-1,
                                height)

        else:
            eden_rendering_done = True

        curr_iter_eden += eden_iter_block

        return curr_iter_eden, eden_rendering_done


    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    For specific sca layer, display one iteration of growth for every sca object
    ****************************************************************** """
    def sca_iter(self, 
                sca_layer, 
                sca_layer_metamesh, 
                curr_iter_sca, 
                sca_rendering_cnt, 
                sca_rendering_done):

        # SCA LAYER MESH ITERATION
        for i in range(len(sca_layer)):

            sca = sca_layer[i]
            sca_mesh = sca_layer_metamesh[i]

            if curr_iter_sca < len(sca.branches):
                self.show_branch(sca, curr_iter_sca, sca_mesh, 1)
            else:
                sca_rendering_cnt += 1

            if sca_rendering_cnt >= len(sca_layer):
                sca_rendering_done = True
                break

        curr_iter_sca += 1

        return curr_iter_sca, sca_rendering_cnt, sca_rendering_done


    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    Using Blender metamesh display branch between parent and current branch
    ****************************************************************** """
    def show_branch(self, sca, iter, metamesh, n_samples):

        branch = sca.branches[iter]

        # NOTE if distance between parent and current branch is large use interpolation
        
        if branch.parent != None:

            element = metamesh.elements.new(type='BALL')
            element.co = branch.position
            element.radius = sca.branch_thickness

            # alternatively add sphere mesh instead of metamesh
            #bpy.ops.mesh.primitive_uv_sphere_add(location=pos, size=0.4, segments=5)



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
    def show_eden_iter(self, metamesh, radius, start_idx, end_idx, height=0):

        print(start_idx, end_idx)

        for curr_idx in range(start_idx, end_idx):
            cell = self.eden.populated_all[curr_idx]

            # move metaball in direction of new cell
            element = metamesh.elements.new()
            loc = self.eden.mapper[(cell[0], cell[1])]
            loc = (loc[0], loc[1], height)
            element.co = loc
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
    lamp_obj.location = (10,10,10)
    bpy.data.lamps['biolampa'].energy = 10
    bpy.data.lamps['biolampa'].distance = 25
    #bpy.data.lamps['biolampa'].gamma = 0.9
    
    # configure camera position and orientation
    bpy.data.objects["Camera"].location = (0, 0, 100)
    bpy.data.objects["Camera"].rotation_euler = (0,0,0)

    # eden sca configuration    
    plate_size = [500,500]
    eden_n_iter = 2200
    eden2_n_iter = 800
    eden_starter = [250,250]
    render_path = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/eden_sca/temp_res'
    render_checkpoint = 5

    es = eden_sca(plate_size = plate_size,
                eden_n_iter = eden_n_iter,
                eden2_n_iter = eden2_n_iter,
                eden_starter = eden_starter,
                render_path = render_path,
                render_checkpoint = render_checkpoint)

    es.display_and_render()


""" ******************************************************************* 
ROOT
******************************************************************** """
main()
