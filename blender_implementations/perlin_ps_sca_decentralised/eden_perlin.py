
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

""" This module creates the Perlin border model.

This module creates the circles with perturbed vertices which serve as an
approximation of Eden model. The perturbed circles are then represented
as Blender mesh objects.

Contains:
	PerlinCircle class

"""

# Blender imports.
import bpy
import bmesh

# Standard imports.
from mathutils import noise
import numpy as np 
import os

class PerlinCircle:

	""" Defines the Perlin border model.

	Attributes:
		center (np.array): center of the perturbed circles
		radius_range (np.array): starting radius, ending radius and step

	Methods:
		__init__()
		grow()
		
	"""

	def __init__(self, 
				 center, 
				 radius_range, 
				 color):
			self.center = center
			self.radius_range = radius_range
			self.color = color

	def __iter_grow(self, param):
		""" Creates one perturbed circle

		Given the parameters, this method is creating one perturbed circle.
		That is it performs one iteration of growth.

		Args:
			param (dict): parameters for creating the perturbed circle.
		
		Yields:
			Blender mesh object: representation of perturbed circle.
			list: contour points.

		"""

		# List of points that will be created on the contour.
		contour_points = []

		# Create empty bmesh to store vertices of circle.
		bm = bmesh.new()
	
		circle_segments = np.linspace(start=0, 
									  stop=2*np.pi, 
									  num=param["n_segments"])

		# For every segment in circle create a perturbed vertex.
		for segment in circle_segments:

			xoff = np.interp(x=np.cos(segment), 
							 xp=[-1,1], 
							 fp=param["noise_range"])

			yoff = np.interp(x=np.sin(segment), 
							 xp=[-1,1], 
						   	 fp=param["noise_range"])

			zoff = param["zoff"]

			pos = np.array([xoff, yoff, zoff])

			noise_val = noise.noise(pos) # NB: noise elem [-1,1]
			noise_val = np.interp(x=noise_val, 
								  xp=[-1,1], 
								  fp=param["noise_amp"])
					
			radius_curr = param["radius"] + noise_val

			x = self.center[0] + radius_curr * np.cos(segment)
			y = self.center[1] + radius_curr * np.sin(segment)
			z = self.center[2]
		
			bm.verts.new(np.array([x,y,z]))
			contour_points.append([x,y,z])

		# Create face from existing vertices.
		bm.faces.new(bm.verts)

		# Add a new mesh data.
		layer_mesh_data = bpy.data.meshes.new(param["layer_name"]+"_data")  

		# add a new empty mesh object using the mesh data.
		layer_mesh_object = bpy.data.objects.new(param["layer_name"]+"_object", layer_mesh_data) 

		# Transform bmesh to mesh.
		bm.to_mesh(layer_mesh_data)
		bm.free()

		# Add material and color.
		material = bpy.data.materials.new(param["layer_name"]+"_material")
		material.diffuse_color = param["color"]
		layer_mesh_object.active_material = material

		return layer_mesh_object, contour_points

	def __configure_params(self, radius, n_radii, curr_iter):
		""" Configures the parameters for next iteration.

		Given the current radius and current iteration configure the rest of
		parameters that are needed for growth.

		Args:
			radius (float): current radius.
			n_radii (int): number of desired radii.
			curr_iter (int): current iteration of growth.

		Yields:
			params (dict): contains configured parameters.

		"""

		# Container for parameters.
		params = {}
                
        # radius.
		params["radius"] = radius

		# n points on a contour.
		# https://stackoverflow.com/questions/11774038/how-to-render-a-circle-with-as-few-vertices-as-possible
		err = 0.001
		th = np.arccos(2 * np.power((1 - err / radius), 2) - 1)
		params["n_segments"] = np.ceil(2 * np.pi / th)

        # Layer name.
		params["layer_name"] = "layer" + str(radius)

        # x and y positions range in Perlin noise.
		params["noise_range"] = [
			0, 
			np.interp(x=curr_iter, xp=[0, n_radii], fp=[0, 20])
			]

		# z position in Perlin noise.
		params["zoff"] = np.interp(x=curr_iter, 
								   xp=[0,n_radii], 
								   fp=[0.23, 0.48])

        # Noise amplitude.
		params["noise_amp"] = [
			np.interp(x=curr_iter, xp=[0, n_radii-1], fp=[0, -1.5]), 
			np.interp(x=curr_iter, xp=[0, n_radii-1], fp=[0, 1.5])
		]

		# Color.
		params["color"] = self.color 

		return params

	def grow(self):
		""" Creates all perturbed circles.

		For every specified radius value, perturbed circle is created.

		Args:
			-

		Yields:
			list of Blender mesh objects: representation of perturbed circles
			list of lists: contour points of all perturbed circles
			list: all radius values

		"""

		# Create list of radii: starting_radius, ending radius, step.
		radii = np.linspace(start=self.radius_range[0], 
							stop=self.radius_range[1], 
							num=self.radius_range[2])

		# List of Blender mesh objects that represent perturbed circles.
		perturbed_circles_mesh = []

		# List of all contour points of all perturbed circles.
		contour_points = []

		curr_iter = 0
		for radius in radii:

			curr_iter += 1

			# Configure the parameters.
			params = self.__configure_params(radius, len(radii), curr_iter)

			# Create perturbed circle for current radius.
			curr_perturbed_circle_mesh, curr_contour_points = self.__iter_grow(params)

			# Save.
			perturbed_circles_mesh.append(curr_perturbed_circle_mesh)
			contour_points.append(curr_contour_points)

		return perturbed_circles_mesh, contour_points, radii
