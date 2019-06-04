from mathutils import noise
import numpy as np 
import bpy
import bmesh
import os
from colorsys import hsv_to_rgb

class PerlinCircle:


        """ ####################################################################################
        CONSTRUCTOR:
        center: np.array([xc, yc, zc])
        radius_range: np.array([max_radius, steps]) -- max radius, steps between 0 and max radius
        shape: np.array([s_x, s_y]), s_x and s_y are [0,1] and determine circle/elipse shape
        ##################################################################################### """
        def __init__(self,
                     center,
                     radius_range,
                     shape
                    ):

                # user defined variables
                self.center = center
                self.radius_range = radius_range
                self.shape = shape


        """ ###################################################################
        For given parameters create blender mesh object that will contain vertices 
        of nosy circle
        ################################################################### """
        def iter_grow(self, param):

                # create empty bmesh to store vertices of circle
                bm = bmesh.new()
        
                # divide circle in segments
                circle_segments = np.linspace(0, 2*np.pi, param["n_segments"])

                for segment in circle_segments:

                        # generate point on a cricle as argument to perlin noise
                        xoff = np.interp(np.cos(segment), [-1,1], param["noise_range"])
                        yoff = np.interp(np.sin(segment), [-1,1], param["noise_range"])
                        zoff = param["zoff"]

                        pos = np.array([xoff, yoff, zoff])

                        # generate noise value
                        noise_val = noise.noise(pos) # NB: noise elem [-1,1]

                        # add to radius
                        radius_curr_x = param["radius_xy"][0] + noise_val
                        radius_curr_y = param["radius_xy"][1] + noise_val

                        # create circle point on nosy radius from center
                        x = self.center[0] + radius_curr_x * np.cos(segment)
                        y = self.center[1] + radius_curr_y * np.sin(segment)
                        z = self.center[2]

                        # add  point to bmesh
                        bm.verts.new(np.array([x,y,z]))

                # add faces and extrude
                # https://blender.stackexchange.com/questions/65359/how-to-create-and-extrude-a-bmesh-face

                # think of this new vertices as bottom of the extruded shape
                bottom_face = bm.faces.new(bm.verts)

                # next we create top via extrude operator, note it doesn't move the new face
                # we make our 1 face into a list so it can be accepted to geom
                top_face = bmesh.ops.extrude_face_region(bm, geom=[bottom_face])

                # here we move all vertices returned by the previous extrusion
                # filter the "geom" list for vertices using list constructor
                bmesh.ops.translate(bm, vec=param["extrude"], verts=[v for v in top_face["geom"] if isinstance(v,bmesh.types.BMVert)])

                bm.normal_update()

                # add a new mesh data
                layer_mesh_data = bpy.data.meshes.new(param["layer_name"]+"_data")  

                # add a new empty mesh object using the mesh data
                layer_mesh_object = bpy.data.objects.new(param["layer_name"]+"_object", layer_mesh_data) 

                # make the bmesh the object's mesh
                # transfer bmesh data do mesh data which is connected to empty mesh object
                bm.to_mesh(layer_mesh_data)
                bm.free()

                # add color
                material = bpy.data.materials.new(param["layer_name"]+"_material")
                material.diffuse_color = param["color"]
                layer_mesh_object.active_material = material

                # return object, data for object can be extracted via eden_layer_mesh_object.data
                return layer_mesh_object


        """ ###################################################################
        configure parameters for current radius
        ################################################################### """
        def configure_params(self, radius, n_radii, iter):

                params = {}
                
                # radius
                radius_x = radius * self.shape[0]
                radius_y = radius * self.shape[1]
                params["radius_xy"] = [radius_x, radius_y]

                # n segments scales with radius
                # https://stackoverflow.com/questions/11774038/how-to-render-a-circle-with-as-few-vertices-as-possible
                err = 0.005
                th = np.arccos(2 * np.power((1 - err / radius), 2) - 1)
                params["n_segments"] = np.ceil(2 * np.pi / th)

                # layer name
                params["layer_name"] = "layer" + str(radius)

                # noise max for perlin arguments x and y (rule of thumb: 1-10) 
                params["noise_range"] = [0, np.interp(iter, [0, n_radii], [0, 20])]
                params["zoff"] = np.interp(iter, [0,n_radii], [0.23, 0.48])

                # extrude
                params["extrude"] = [0,0,np.interp(n_radii-iter, [0,n_radii], [0.01,0.5])]

                # color
                h = 30.0/360.0
                s = 50.0/100.0
                v = 50.0/100.0
                #s = np.interp(iter, [0, n_radii], [45,55])
                params["color"] = hsv_to_rgb(h,s,v)

                return params



        """ ###################################################################
        vary initial parameters to achieve growth
        result will be list of mesh objects in different stadium of growth
        ################################################################### """
        def grow(self):

                # create list of radii: starting_radius, ending radius, step
                radii = np.linspace(0.1, self.radius_range[0], self.radius_range[1])

                # list of blender meshes that represent circle growth
                growth_phases = []
                iter = 0

                # every iteration represents radius
                for radius in radii:

                        iter += 1

                        # configure params
                        params = self.configure_params(radius, len(radii), iter)

                        # run circle generation for curr params and radius
                        growth_phase = self.iter_grow(params)

                        # save
                        growth_phases.append((radius, growth_phase))

                return growth_phases


