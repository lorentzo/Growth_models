import bpy
import numpy as np 
import bmesh
import os
from colorsys import hsv_to_rgb
from eden_perlin import PerlinCircle

class PerlinPSBorder:

    def __init__(
        self, 
        center, 
        radius_range,
        color_perlin_border,
        color_ps):

        self.center = center 
        self.radius_range = radius_range
        self.color_perlin_border = color_perlin_border
        self.color_ps = color_ps



    """ #######################################################################################
    create blender mesh object with particles system using contour points and dupli object
    for particle system
    ######################################################################################## """ 
    def define_object(self, points, name, ps_object):

        # create bmesh and add points
        bm = bmesh.new()
        for point in points:
            bm.verts.new(point)
            
        # create mesh from bmesh
        mesh_data = bpy.data.meshes.new(name+"_data")
        mesh_obj = bpy.data.objects.new(name+"_obj", mesh_data)
        bm.to_mesh(mesh_data)
        bm.free()
        
        # add particle system to mesh
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

        return mesh_obj

    """ #######################################################################################
     ps dupli object
    ######################################################################################## """ 
    def create_dupli_obj(self):

        # create texture for displacement
        bpy.data.textures.new('diplace_tex', type='VORONOI')

        # create sphere (far from camera view)
        bpy.ops.mesh.primitive_uv_sphere_add(location=[1000,10,10], size=1)

        # add displacement
        bpy.ops.object.modifier_add(type='DISPLACE')
        bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["diplace_tex"]

        # reference dupli object
        dupli_obj = bpy.context.object
        dupli_obj.scale = [2,2,0.1]

        # add material/color
        material = bpy.data.materials.new("dupli_material")
        material.diffuse_color = self.color_ps
        dupli_obj.active_material = material

        return dupli_obj

    """ #######################################################################################
    creates perlin border layers
    creates blender mesh object with particle system
    ######################################################################################## """ 
    def give_perlin_ps(self):

        # define perlin circles
        ep = PerlinCircle(
            center=self.center, 
            radius_range=self.radius_range,
            color=self.color_perlin_border)
            
        # grow
        perlin_layers, perlin_contour, radii = ep.grow()

        # create dupli object for particle in ps
        dupli_obj = self.create_dupli_obj()

        # add ps for every perlin circle
        ps_layers = []
        for pc_idx in range(len(perlin_contour)):
            layer = self.define_object(perlin_contour[pc_idx], "layer"+str(pc_idx), dupli_obj)
            bpy.context.scene.objects.link(layer)
            ps_layers.append(layer)

        return perlin_layers, ps_layers, radii

    """ #######################################################################################
    emerge particle system size
    ######################################################################################## """ 
    def emerge_ps_area(self):
        pass


