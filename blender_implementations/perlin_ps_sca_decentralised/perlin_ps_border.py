# -*- coding: utf-8 -*-
""" This model creates the Perlin border model with particle system.

This module uses the eden_perlin module which create the Perlin border model.
The created Perlin border model is enhanced with particle system.

Contains:
    PerlinPSBorder class
"""

# Project specific imports.
from eden_perlin import PerlinCircle

# Blender imports.
import bmesh
import bpy

# Standard imports.
import numpy as np 
import os
from colorsys import hsv_to_rgb

class PerlinPSBorder:

    """ Defines enhanced Perlin border model.

    Attributes:
        center (np.array): center of enhanced Perlin border model.
        radius_range (np.array): starting radius, ending radius and step.
        color_perlin_border (np.array): color of Perlin border model.
        color_ps (np.array): color of the particle system.

    Methods:
        __init__()
        give_perlin_ps()

    """

    def __init__(self, 
                 center, 
                 radius_range,
                 color_perlin_border,
                 color_ps):

        self.center = center 
        self.radius_range = radius_range
        self.color_perlin_border = color_perlin_border
        self.color_ps = color_ps
 
    def __define_object(self, points, name, ps_object):

        """ Creates the Blender mesh object with particle system.

        Given the points for particles and particle object crates the
        mesh.

        Args:
            points (list): points of countour where particles will be initialized
            name (string): name of mesh
            ps_object: Blender mesh object that will particles take form

        Yield:
            Blender mesh object: mesh object with particle system.

        """

        # Create bmesh and add points.
        bm = bmesh.new()
        for point in points:
            bm.verts.new(point)
            
        # Create mesh from bmesh.
        mesh_data = bpy.data.meshes.new(name+"_data")
        mesh_obj = bpy.data.objects.new(name+"_obj", mesh_data)
        bm.to_mesh(mesh_data)
        bm.free()
        
        # Add particle system to the mesh.
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

    def __create_dupli_obj(self):

        """ Creates the Blender mesh object that particles use for representation

        Particles initialy are zero dimensional. Therefore, for rendering, particles
        should have a mesh shape. This function is creation a mesh object that
        every particle will use.

        Args:
            -

        Yields:
            Blender mesh object

        """

        # Create the texture for vectex displacement.
        bpy.data.textures.new('diplace_tex', type='VORONOI')

        # Create mesh sphere object (far from camera view).
        bpy.ops.mesh.primitive_uv_sphere_add(location=[1000,10,10], size=1)

        # Add a displacement of sphere vertices using the displacement texture.
        bpy.ops.object.modifier_add(type='DISPLACE')
        bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["diplace_tex"]

        # Reference dupli object.
        dupli_obj = bpy.context.object
        dupli_obj.scale = [2,2,0.1]

        # Add material/color.
        material = bpy.data.materials.new("dupli_material")
        material.diffuse_color = self.color_ps
        dupli_obj.active_material = material

        return dupli_obj

    def give_perlin_ps(self):

        """ Creates Perlin border model and particle system.
        
        First, the Perlin border model is created. Using the points of contour of
        the every perturbed circle, particle system is initalised.

        Args:
            -

        Yield:
            list of Blender mesh object: perturbed circles
            list of Blender mehs objects: particle systems for every perturbed circle
            list: radius values

        """

        # Define the Perlin border model and grow it.
        ep = PerlinCircle(center=self.center, 
                          radius_range=self.radius_range,
                          color=self.color_perlin_border)
            
        perlin_layers, perlin_contour, radii = ep.grow()

        # Create dupli object for particles.
        dupli_obj = self.__create_dupli_obj()

        # Add PS for every perlin circle.
        ps_layers = []
        for pc_idx in range(len(perlin_contour)):
            layer = self.__define_object(perlin_contour[pc_idx], "layer"+str(pc_idx), dupli_obj)
            bpy.context.scene.objects.link(layer)
            ps_layers.append(layer)

        return perlin_layers, ps_layers, radii