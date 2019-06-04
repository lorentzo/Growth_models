from mathutils import noise
import numpy as np 
import bpy
import bmesh
import os

""" ###################################################################
CLASS:
defines:
        + blender object in shape of perlin 
		circle that needs to be attached to scene
        + points for every contour
        + list or radii used
################################################################### """

class PerlinCircle:


        """ ##############################################################
        CONSTRUCTOR:
        center: np.array([xc, yc, zc])
        radius_range: np.array([lower, upper, step]) 
			-- starting radius, ending radius and step
        ############################################################## """
        def __init__(self, center, radius_range, color):

                # user defined variables
                self.center = center
                self.radius_range = radius_range
                self.color = color


        """ ####################################################
        For given parameters create blender mesh 
        object that will contain vertices  of nosy circle
        #################################################### """
        def iter_grow(self, param):

                # container for points on contour
                contour_points = []

                # create empty bmesh to store vertices of circle
                bm = bmesh.new()
        
                # divide circle in segments
                circle_segments = np.linspace(0, 
					      2*np.pi, 
					      param["n_segments"])

                for segment in circle_segments:

                        # generate point on a cricle as argument to perlin noise
                        xoff = np.interp(np.cos(segment), 
					 [-1,1], 
				  	 param["noise_range"])

                        yoff = np.interp(np.sin(segment), 
					 [-1,1], 
					 param["noise_range"])

                        zoff = param["zoff"]

                        pos = np.array([xoff, yoff, zoff])

                        # generate noise value
                        noise_val = noise.noise(pos) # NB: noise elem [-1,1]
                        noise_val = np.interp(noise_val, 
					      [-1,1], 
					      param["noise_amp"])
                        
                        # add to radius
                        radius_curr = param["radius"] + noise_val

                        # create circle point on nosy radius from center
                        x = self.center[0] + radius_curr * np.cos(segment)
                        y = self.center[1] + radius_curr * np.sin(segment)
                        z = self.center[2]

                        # add  point to bmesh and container
                        bm.verts.new(np.array([x,y,z]))
                        contour_points.append([x,y,z])

                # add faces 
                bm.faces.new(bm.verts)

                # add a new mesh data
                layer_mesh_data = bpy.data.meshes.new(
						param["layer_name"]+"_data")  

                # add a new empty mesh object using the mesh data
                layer_mesh_object = bpy.data.objects.new(
					param["layer_name"]+"_object", 
					layer_mesh_data) 

                # make the bmesh the object's mesh
                # transfer bmesh data do mesh data which 
		# is connected to empty mesh object
                bm.to_mesh(layer_mesh_data)
                bm.free()

                # add color
                material = bpy.data.materials.new(
				param["layer_name"]+"_material")

                material.diffuse_color = param["color"]
                layer_mesh_object.active_material = material

                # return object, data for object can 
		# be extracted via eden_layer_mesh_object.data
                return layer_mesh_object, contour_points

        """ ###############################################
        configure parameters for current radius
        ############################################### """
        def configure_params(self, radius, n_radii, curr_iter):

                params = {}
                
                # radius
                params["radius"] = radius

                # n segments scales with radius
                # https://stackoverflow.com/questions/11774038/how-to-render-a-circle-with-as-few-vertices-as-possible
                err = 0.001
                th = np.arccos(2 * np.power((1 - err / radius), 2) - 1)
                params["n_segments"] = np.ceil(2 * np.pi / th)

                # layer name
                params["layer_name"] = "layer" + str(radius)

                # noise max for perlin arguments x and y (rule of thumb: 1-10) 
                params["noise_range"] = [0, np.interp(curr_iter, 
					             [0, n_radii], 
						     [0, 20])]

                params["zoff"] = np.interp(curr_iter, 
				           [0,n_radii], 
					   [0.23, 0.48])

                # noise amp
                params["noise_amp"] = [np.interp(curr_iter, [0, n_radii-1], [0, -1.5]), 
					np.interp(curr_iter, [0, n_radii-1], [0, 1.5])]

                # color
                params["color"] = self.color 

                return params

        """ ###################################################################
        vary initial parameters to achieve growth
        result will be list of mesh objects in different stadium of growth
        ################################################################### """
        def grow(self):

                # create list of radii: starting_radius, ending radius, step
                radii = np.linspace(self.radius_range[0], 
				    self.radius_range[1], 
				    self.radius_range[2])

                # list of blender meshes that represent circle growth
                growth_phases = []
                curr_iter = 0

                # list of all contour points
                contour_points_all = []

                # every iteration represents radius
                for radius in radii:

                        curr_iter += 1

                        # configure params
                        params = self.configure_params(radius, len(radii), curr_iter)

                        # run circle generation for curr params and radius
                        growth_phase, contour_points = self.iter_grow(params)

                        # save
                        growth_phases.append(growth_phase)
                        contour_points_all.append(contour_points)

                return growth_phases, contour_points_all, radii

