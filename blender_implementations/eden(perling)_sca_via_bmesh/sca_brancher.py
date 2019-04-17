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
            
            # convert mesh to curve and add bevel
            bpy.context.scene.layers[0] = False
            bpy.context.scene.layers[3] = True
            """
            bpy.ops.curve.primitive_nurbs_circle_add(radius=0.04)
            bevel = bpy.context.object
            
            scene.objects.link(sca_object) 
            sca_object.select = True
            bpy.context.scene.objects.active = sca_object
            bpy.ops.object.convert(target='CURVE')
            sca_object.data.bevel_object = bevel
            """

            sca_forest.append(sca_object)

        return sca_forest


# sca circle layer
scaCL = SCACircleBrancher(center=[0,0,0],
                          n_sca_trees=10,
                          root_circle_radius=10,
                          leaves_spread=np.array([10,10,0]),
                          n_leaves=20,
                          name='scaCL')

sca_layers = scaCL.configure_sca_forest()

bpy.context.scene.layers[0] = True
for sca_layer in sca_layers:
    print(sca_layer)
    bpy.context.scene.objects.link(sca_layer)

