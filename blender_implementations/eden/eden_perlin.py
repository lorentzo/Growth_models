from mathutils import noise
import numpy as np 
import bpy
import bmesh
import os

class PerlinCircle:


        """ ####################################################################################
        CONSTRUCTOR:
        center: np.array([xc, yc, zc])
        radius_range: np.array([lower, upper, step]) -- starting radius, ending radius and step
        ##################################################################################### """
        def __init__(self,
                     center,
                     radius_range,

                    ):

                self.center = center
                self.radius_range = radius_range


        """ ###################################################################
        For given parameters create blender mesh object that will contain vertices 
        of nosy circle
        ################################################################### """
        def iter_grow(self, param):

                # create empty bmesh
                bm = bmesh.new()
        
                # divide circle in segments
                circle_segments = np.linspace(0, 2*np.pi, param["n_segments"])

                for segment in circle_segments:

                        # generate point on a cricle as argument to perlin noise
                        xoff = np.interp(np.cos(segment), [-1,1], param["noise_max"])
                        yoff = np.interp(np.sin(segment), [-1,1], param["noise_max"])
                        zoff = param["zoff"]

                        pos = np.array([xoff, yoff, zoff])

                        # generate noise value
                        noise_val = noise.noise(pos) # NB: noise elem [-1,1]

                        # add to radius
                        radius_curr = param["radius"] + noise_val

                        # create circle point on nosy radius from center
                        x = self.center[0] + radius_curr * np.cos(segment)
                        y = self.center[1] + radius_curr * np.sin(segment)
                        z = self.center[2]

                        # add  point to bmesh
                        bm.verts.new(np.array([x,y,z]))

                # add a new mesh data
                layer_mesh_data = bpy.data.meshes.new(param["layer_name"]+"_data")  

                # add a new empty mesh object using the mesh data
                layer_mesh_object = bpy.data.objects.new(param["layer_name"]+"_object", layer_mesh_data) 

                # make the bmesh the object's mesh
                # transfer bmesh data do mesh data which is connected to empty mesh object
                bm.to_mesh(layer_mesh_data)
                bm.free()

                # return object, data for object can be extracted via eden_layer_mesh_object.data
                return layer_mesh_object


        """ ###################################################################
        configure parameters for current radius
        ################################################################### """
        def configure_params(self, radius, n_radii):

                params = {}
                
                # radius
                params["radius"] = radius

                # n segments scales with radius
                # https://stackoverflow.com/questions/11774038/how-to-render-a-circle-with-as-few-vertices-as-possible
                err = 0.01
                th = np.arccos(2 * np.power((1 - err / radius), 2) - 1)
                params["n_segments"] = np.ceil(2 * np.pi / th)

                # layer name
                params["layer_name"] = "layer" + str(radius)

                # noise max for perlin arguments x and y (rule of thumb: 1-10) 
                params["noise_max"] = [0, np.interp(radius, [0, n_radii], [0, 10])]
                params["zoff"] = np.pi

                return params



        """ ###################################################################
        vary initial parameters to achieve growth
        result will be list of mesh objects in different stadium of growth
        ################################################################### """
        def grow(self):

                # create list of radii: starting_radius, ending radius, step
                radii = list(range(self.radius_range[0], self.radius_range[1], self.radius_range[2]))

                # list of blender meshes that represent circle growth
                growth_phases = []

                # every iteration represents radius
                for radius in radii:

                        # configure params
                        params = self.configure_params(radius, len(radii))

                        # run circle generation for curr params and radius
                        growth_phase = self.iter_grow(params)

                        # save
                        growth_phases.append(growth_phase)

                return growth_phases


        """ ###################################################################
        add faces to mesh vertices and render iterations
        ################################################################### """
        def render(self, scene, render_out):

                growth_phases = self.grow()
                iter = 0

                for phase_object in growth_phases:

                        iter += 1

                        # add object to scene
                        scene.objects.link(phase_object)  

                        # add faces/edges (also can randomise vertices a bit)
                        scene.objects.active = phase_object
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_mode(type='VERT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.edge_face_add()
                        bpy.ops.object.mode_set(mode='OBJECT')

                        # render
                        bpy.context.scene.render.filepath = os.path.join(render_out, str(iter))
                        bpy.ops.render.render(write_still=True)



""" ###################################################################
main
################################################################### """
def main():    

    # get scene
    scene = bpy.context.scene

    # configure camera position and orientation
    bpy.data.objects["Camera"].location = (0, 0, 50)
    bpy.data.objects["Camera"].rotation_euler = (0,0,0)

    # render out
    render_out = '/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/eden_perlin/tmp/'

    ep = PerlinCircle(center=np.array([0,0,0]), radius_range=np.array([1, 20, 2]))
    ep.render(scene, render_out)
    

     
""" ###################################################################
root
################################################################### """
main()

 
"""
        #ZANIMLJIVO: ako ne koristis mapiranje za noise dobivas latice!
"""