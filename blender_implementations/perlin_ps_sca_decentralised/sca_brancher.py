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
                 leaf_center_radius,
                 leaves_spread,
                 n_leaves,
                 branch_thickness_max,
                 bevel_radius_delta,
                 name,
                 color):

        # user defined
        self.center = center
        self.n_sca_trees = n_sca_trees
        self.root_circle_radius = root_circle_radius
        self.leaf_center_radius = leaf_center_radius
        self.leaves_spread = leaves_spread
        self.n_leaves = n_leaves
        self.name = name
        self.color = color

        # additional
        self.sca_forest = []
        self.bevel_radius = 0
        self.bevel_radius_delta = bevel_radius_delta
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

            # configure sca root position
            xr = self.center[0] + np.cos(segment * n) * self.root_circle_radius
            yr = self.center[1] + np.sin(segment * n) * self.root_circle_radius
            zr = self.center[2] + 0

            # configure sca leaf center position
            xl = self.center[0] + np.cos(segment * n) * self.leaf_center_radius
            yl = self.center[1] + np.sin(segment * n) * self.leaf_center_radius
            zl = self.center[2] + 0

            sca = SCA(root_position=[xr,yr,zr],
                        leaves_cloud_center=[xl, yl, zl],
                        leaves_spread=self.leaves_spread,
                        n_leaves=self.n_leaves,
                        growth_dist={"min":0.5,"max":4}) # play with params

            # grow
            sca.grow()

            # create mesh
            bm = bmesh.new()

            for branch in sca.branches:
                if branch.parent == None:
                    continue
                v1 = bm.verts.new(branch.position)
                v2 = bm.verts.new(branch.parent.position)
                interpolated = self.interpolate_nodes(v1, v2, 2, 0.5, bm)
                for i in range(len(interpolated)-1):
                    bm.edges.new((interpolated[i], interpolated[i+1]))
                
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
            
        
        
    def interpolate_nodes(self, v1, v2, n_nodes, rand_amplitude, bm):
        
        helper_nodes = []
        
        for t in range(n_nodes+1):

            # interpolate
            x = (1 - t / n_nodes) * v1.co[0] + (t / n_nodes) * v2.co[0]
            y = (1 - t / n_nodes) * v1.co[1] + (t / n_nodes) * v2.co[1]
            z = (1 - t / n_nodes) * v1.co[2] + (t / n_nodes) * v2.co[2]

            # add random noise
            x += np.random.rand() * rand_amplitude
            y += np.random.rand() * rand_amplitude
            #z += np.random.rand() * rand_amplitude

            helper_nodes.append(bm.verts.new([x,y,z]))

        return helper_nodes
        


    def emerge_sca_volume(self):

        new_radius = self.bevel_object.scale[0] + self.bevel_radius_delta
        print(new_radius,self.bevel_radius_max)

        if new_radius < self.bevel_radius_max:

            self.bevel_object.scale = (new_radius, new_radius, new_radius)

            return False # not finished

        else:

            return True # finished



