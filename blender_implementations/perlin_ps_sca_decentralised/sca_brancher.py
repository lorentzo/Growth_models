
#
# This source file is part of Growth_models.
# Visit https://github.com/lorentzo/Growth_models for more information.
#
# This software is released under MIT licence.
#
# Copyright (c) Lovro Bosnar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# -*- coding: utf-8 -*-

""" Circular branching of SCA model.

This module uses the sca module and creates the circular growth.

Contains:
    SCACircleBrancher class

"""

#Project specific imports.
from sca import SCA

# Blender imports
import bpy
import bmesh

# Standard imports.
import numpy as np
import os


class SCACircleBrancher:
    """ Defines the circular growth of SCA model.

    Attributes:
        center (np.array): center of circular SCA.
        n_sca_trees (int):  number of SCA trees in circular SCA.
        root_circle_radius (float): radius of circle where roots will be.
        leaf_center_radius (float): radius of circle where leaves centers will be.
        leaves_spread (np.array): spread of leaves in x,y,z direction.
        n_leaves (int): number of leaves in every SCA tree.
        branch_thickness_max (float): max thickness of a branch.
        bevel_radius_delta (float): increase of thickness in every iteration.
        name (string): name of circular SCA object.
        color (np.array): color of SCA circular object.

    Methods:
        __init__()
        initialize_sca_forest()
        emerge_sca_volume()

    """
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

        # User defined.
        self.center = center
        self.n_sca_trees = n_sca_trees
        self.root_circle_radius = root_circle_radius
        self.leaf_center_radius = leaf_center_radius
        self.leaves_spread = leaves_spread
        self.n_leaves = n_leaves
        self.name = name
        self.color = color

        # Additional.
        self.sca_forest = []
        self.bevel_radius = 0
        self.bevel_radius_delta = bevel_radius_delta
        self.bevel_radius_max = branch_thickness_max
        self.bevel_object = None

    def initialize_sca_forest(self, scene):
        """ Confiure and grow the set of the SCA objects.

        Args:
            scene (Blender scene object): scene where SCA objects will be placed.

        Yields:
            list of Blender curve objects.

        """

        segment = 2 * np.pi / self.n_sca_trees

        # Create bevel object for volume (ini: 0 volume).
        bpy.ops.curve.primitive_nurbs_circle_add()
        bpy.context.object.scale = (0,0,0)
        self.bevel_object = bpy.context.object

        # For every SCA model.
        for n in range(self.n_sca_trees):

            # Configure SCA root position.
            xr = self.center[0] + np.cos(segment * n) * self.root_circle_radius
            yr = self.center[1] + np.sin(segment * n) * self.root_circle_radius
            zr = self.center[2] + 0

            # Configure SCA leaf center position.
            xl = self.center[0] + np.cos(segment * n) * self.leaf_center_radius
            yl = self.center[1] + np.sin(segment * n) * self.leaf_center_radius
            zl = self.center[2] + 0

            # Configure SCA and grow.
            sca = SCA(root_position=[xr,yr,zr],
                      leaves_cloud_center=[xl, yl, zl],
                      leaves_spread=self.leaves_spread,
                      n_leaves=self.n_leaves)

            sca.grow()

            # Create mesh.
            bm = bmesh.new()

            for branch in sca.branches:
                if branch.parent == None:
                    continue
                v1 = bm.verts.new(branch.position)
                v2 = bm.verts.new(branch.parent.position)
                interpolated = self.__interpolate_nodes(v1, v2, 4, 0.5, bm)
                for i in range(len(interpolated)-1):
                    bm.edges.new((interpolated[i], interpolated[i+1]))
                
            # Add a new mesh data.
            sca_data = bpy.data.meshes.new(self.name+str(n)+"_data")  

            # Add a new empty mesh object using the mesh data.
            sca_object = bpy.data.objects.new(self.name+str(n)+"_object", sca_data) 
            
            # Make the bmesh the object's mesh.
            # Transfer bmesh data do mesh data which is connected to empty mesh object.
            bm.to_mesh(sca_data)
            bm.free()
            
            # Add sca object to scene, convert to curve, add bevel.
            scene.objects.link(sca_object) 
            sca_object.select = True
            bpy.context.scene.objects.active = sca_object
            bpy.ops.object.convert(target='CURVE')
            sca_object.data.bevel_object = self.bevel_object

            # Add color.
            material = bpy.data.materials.new(self.name+str(n)+"_material")
            material.diffuse_color = self.color
            sca_object.active_material = material

            # Store
            self.sca_forest.append(sca_object)
            
    def __interpolate_nodes(self, v1, v2, n_nodes, rand_amplitude, bm):
        """ Interpolates nodes between two existing nodes.

        Given the two existing nodes, interpolate additional nodes with a small
        amout of noise.

        Args:
            v1 (Blender vertex object): first node
            v2 (Blender vertex object): second node
            n_nodes (int): number of nodes to interpolate
            rand_amlitude (float): noise amiplitude
            bm (Blender bmesh object): container for created nodes

        Yields:
            list of Blender vertex objects: interpolated nodes

        """
        
        helper_nodes = []
        
        for t in range(n_nodes+1):

            # Interpolate.
            x = (1 - t / n_nodes) * v1.co[0] + (t / n_nodes) * v2.co[0]
            y = (1 - t / n_nodes) * v1.co[1] + (t / n_nodes) * v2.co[1]
            z = (1 - t / n_nodes) * v1.co[2] + (t / n_nodes) * v2.co[2]

            # Add random noise.
            x += np.random.rand() * rand_amplitude
            y += np.random.rand() * rand_amplitude
            #z += np.random.rand() * rand_amplitude

            helper_nodes.append(bm.verts.new([x,y,z]))

        return helper_nodes
        
    def emerge_sca_volume(self):
        """ Increases the radius of bevel object.

        Increasing the radius of bevel object results in increasing the
        branch radius.
        
        """

        new_radius = self.bevel_object.scale[0] + self.bevel_radius_delta

        if new_radius < self.bevel_radius_max:

            self.bevel_object.scale = (new_radius, new_radius, new_radius)

            return False # not finished

        else:

            return True # finished
