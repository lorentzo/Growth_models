import bpy
import numpy as np
import bmesh
from sca import SCA
import os
class SCACircleBrancher:

    def __init__(self,
                 center,
                 n_sca_trees,
                 root_circle_radius,
                 leaves_spread,
                 n_leaves,
                 branch_thickness_max,
                 name,
                 color):

        # user defined
        self.center = center
        self.n_sca_trees = n_sca_trees
        self.root_circle_radius = root_circle_radius
        self.leaves_spread = leaves_spread
        self.n_leaves = n_leaves
        self.name = name
        self.color = color

        # additional
        self.sca_forest = []
        self.bevel_radius = 0
        self.bevel_radius_delta = 0.01
        self.bevel_radius_max = branch_thickness_max
        self.bevel_object = None

    """ #########################################################################
    Configure set of sca objects 
    grow configured set of sca objects
    create curve from mesh from bmesh of sca objects and add to scene
    Created curves will be invisible to render so increase volume during iterations 
        to make them appear
    ######################################################################### """
    def initialize_sca_forest(self, scene):

        segment = 2 * np.pi / self.n_sca_trees

        # create bevel object for volume (ini: 0 volume)
        bpy.ops.curve.primitive_nurbs_circle_add()
        bpy.context.object.scale = (0,0,0)
        self.bevel_object = bpy.context.object

        for n in range(self.n_sca_trees):

            # configure sca
            x = self.center[0] + np.cos(segment * n) * self.root_circle_radius
            y = self.center[1] + np.sin(segment * n) * self.root_circle_radius
            z = self.center[2] + 0

            sca = SCA(root_position=[x,y,z],
                        leaves_cloud_center=self.center,
                        leaves_spread=self.leaves_spread,
                        n_leaves=self.n_leaves,
                        growth_dist={"min":0.5,"max":4}) # test

            # grow
            sca.grow()

            # create mesh
            bm = bmesh.new()

            for branch in sca.branches:
                if branch.parent == None:
                    continue
                v1 = bm.verts.new(branch.position)
                v2 = bm.verts.new(branch.parent.position)
                bm.edges.new((v1,v2))
                
            # add a new mesh data
            sca_data = bpy.data.meshes.new(self.name+str(n)+"_data")  

            # add a new empty mesh object using the mesh data
            sca_object = bpy.data.objects.new(self.name+str(n)+"_object", sca_data) 
            
            # make the bmesh the object's mesh
            # transfer bmesh data do mesh data which is connected to empty mesh object
            bm.to_mesh(sca_data)
            bm.free()
            
            # add sca object to scene, convert to curve, add bevel
            scene.objects.link(sca_object) 
            sca_object.select = True
            bpy.context.scene.objects.active = sca_object
            bpy.ops.object.convert(target='CURVE')
            sca_object.data.bevel_object = self.bevel_object

            # add color
            material = bpy.data.materials.new(self.name+str(n)+"_material")
            material.diffuse_color = self.color
            sca_object.active_material = material


            # store sca_objects
            self.sca_forest.append(sca_object)


    def emerge_sca_volume(self):

        new_radius = self.bevel_object.scale[0] + self.bevel_radius_delta
        print(new_radius,self.bevel_radius_max)

        if new_radius < self.bevel_radius_max:

            self.bevel_object.scale = (new_radius, new_radius, new_radius)

            return False # not finished

        else:

            return True # finished




"""
# sca circle layer
scaCL = SCACircleBrancher(center=[0,0,0],
                          n_sca_trees=10,
                          root_circle_radius=10,
                          leaves_spread=np.array([10,10,0]),
                          n_leaves=20,
                          name='scaCL')

sca_layers = scaCL.configure_sca_forest()

# link to the scene and add builder modifier
for sca_layer in sca_layers:
    print(sca_layer)
    bpy.context.scene.objects.link(sca_layer)
    sca_layer.select = True
    bpy.context.scene.objects.active = sca_layer
    bpy.ops.object.modifier_add(type='BUILD')
    bpy.context.object.modifiers['Build'].frame_duration=10
    bpy.context.object.modifiers['Build'].frame_start=0


frame = 0
render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/eden_sca_bmesh/tmp/'
while True:
    if frame < -10:
            break
    for sca_layer in sca_layers:
        sca_layer.select = True
        bpy.context.scene.objects.active = sca_layer
        bpy.context.object.modifiers['Build'].frame_start = frame

    frame -= 0.5

    # render
    bpy.context.scene.render.filepath = os.path.join(render_out, str(frame))
    bpy.ops.render.render(write_still=True)
        
"""


