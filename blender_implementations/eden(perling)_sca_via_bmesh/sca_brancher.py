import bpy
import numpy as np
import bmesh
from sca import SCA

class SCACircleBrancher:

    def __init__(self,
                 center,
                 n_sca_trees,
                 root_circle_radius,
                 leaves_spread,
                 n_leaves,
                 name):

        self.center = center
        self.n_sca_trees = n_sca_trees
        self.root_circle_radius = root_circle_radius
        self.leaves_spread = leaves_spread
        self.n_leaves = n_leaves
        self.name = name

    
    def configure_sca_forest(self):

        sca_forest = []
        segment = 2 * np.pi / self.n_sca_trees
        scene = bpy.context.scene

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
            scene.objects.link(sca_object) 
            # convert mesh to curve and add bevel
            #bpy.ops.object.mode_set(mode='OBJECT')
            bpy.data.objects[self.name+str(n)+"_object"].select = True
            bpy.context.scene.objects.active = sca_object
            bpy.ops.object.convert(target='CURVE')
            #bpy.context.space_data.context = 'DATA'
            bpy.context.object.data.fill_mode = 'FULL'
            bpy.context.object.bevel_depth = 0.04
            #bpy.data.curves[self.name+str(n)+"_object"].fill_mode = 'FULL'
            #bpy.data.curves[self.name+str(n)+"_object"].bevel_dept = 0.05

            sca_forest.append(sca_object)

        return sca_forest