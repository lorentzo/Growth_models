import bpy
import numpy as np 
import bmesh
import os
from eden_perlin_ps import PerlinCircle

class EDEN_PERLIN_PS_BORDER:

    def __init__(self, center, radius_range):
        self.center = center 
        self.radius_range = radius_range

    def define_object(self, points, name, ps_object):

        # create bmesh
        bm = bmesh.new()
        for point in points:
            bm.verts.new(point)
            
        # create mesh from bmesh
        mesh_data = bpy.data.meshes.new(name+"_data")
        mesh_obj = bpy.data.objects.new(name+"_obj", mesh_data)
        bm.to_mesh(mesh_data)
        bm.free()
        
        # add particle system
        mesh_obj.modifiers.new(name+"_ps", type='PARTICLE_SYSTEM')
        mesh_obj_ps = mesh_obj.particle_systems[0]
        mesh_obj_ps.settings.emit_from = 'VERT'
        mesh_obj_ps.settings.particle_size = 0.0
        mesh_obj_ps.settings.render_type = 'OBJECT'
        mesh_obj_ps.settings.dupli_object = ps_object
        mesh_obj_ps.settings.frame_start = 1
        mesh_obj_ps.settings.frame_end = 0
        mesh_obj_ps.settings.use_emit_random = False
        mesh_obj_ps.settings.count = len(points)

        return mesh_obj # can reference data and ps

    def create_dupli_obj(self):

        # ps object
        # create texture for displacement
        bpy.data.textures.new('diplace_tex', type='VORONOI')
        # create sphere
        bpy.ops.mesh.primitive_uv_sphere_add(location=[10,10,10], size=1)
        # add displacement
        bpy.ops.object.modifier_add(type='DISPLACE')
        bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["diplace_tex"]
        # reference dupli object
        dupli_obj = bpy.context.object
        dupli_obj.scale = [2,2,0.1]

        return dupli_obj


    def give_perlin_ps(self):

        # create perlin circles
        ep = PerlinCircle(center=self.center, 
                            radius_range=self.radius_range,
                            shape=np.array([1,1]))
            
        perlin_layers, perlin_contour, radii = ep.grow()


        # create ps
        dupli_obj = self.create_dupli_obj()

        # add ps for every perlin circle
        ps_layers = []
        cnt = 1
        for points in perlin_contour:
            layer = self.define_object(points, "layer"+str(cnt), dupli_obj)
            bpy.context.scene.objects.link(layer)
            ps_layers.append(layer)
            cnt += 1

        return perlin_layers, ps_layers, radii



