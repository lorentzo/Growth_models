import bpy
import bmesh
import numpy as np 

class Particle:

    def __init__(self, position):

        self.position = np.array(position)
        bpy.ops.mesh.primitive_uv_sphere_add(size=0.2, location=position)


class Organism:

    def __init__(self):

        self.generations = 2
        self.radius = 5

    def calculate_mesh(self, particles):

        bm = bmesh.new()

        for particle in particles:
            bm.verts.new(particle.position)

        bm.faces.new(bm.verts)

        # add a new mesh data
        layer_mesh_data = bpy.data.meshes.new("data")  

        # add a new empty mesh object using the mesh data
        layer_mesh_object = bpy.data.objects.new("object", layer_mesh_data) 

        # make the bmesh the object's mesh
        # transfer bmesh data do mesh data which is connected to empty mesh object
        bm.to_mesh(layer_mesh_data)
        bm.free()

        # add color
        material = bpy.data.materials.new("material")
        material.diffuse_color = [0.1,0.2,0.3]
        layer_mesh_object.active_material = material

        # add to scene
        bpy.context.scene.objects.link(layer_mesh_object)

        return layer_mesh_object




    def grow(self):

        active_particles = []
        active_particles.append(Particle([0,0,0]))
        meshes = []

        for l in range(self.generations):

            new_active_particles = []

            for particle in active_particles:

                n_new_particles = np.random.randint(low=10, high=20)
                segments = np.linspace(0, np.pi*2, n_new_particles)

                curr_particle_children = []
                for n_particle in range(n_new_particles):

                    # dostance of a new particle from its parent
                    r = self.radius / np.power(2, l)
                    dr = np.random.rand() * self.radius / np.power(2, l+1)
                    rand = np.random.rand()
                    if rand > 0.5:
                        r += dr
                    else:
                        r -= dr

                    # angle of a new paricle
                    phi = segments[n_particle] + np.pi / n_new_particles + np.random.rand() * np.pi/2 / n_new_particles

                    # position of a new particle
                    x = particle.position[0] + r * np.cos(phi)
                    y = particle.position[1] + r * np.sin(phi)

                    new_particle = Particle([x,y,0])
                    curr_particle_children.append(new_particle)
                    new_active_particles.append(new_particle)

                curr_particle_mesh = self.calculate_mesh(curr_particle_children)
                meshes.append(curr_particle_mesh)

            active_particles = new_active_particles


def main():

    org = Organism()
    org.grow()

main()









