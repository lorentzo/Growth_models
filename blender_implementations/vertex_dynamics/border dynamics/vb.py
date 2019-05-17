import numpy as np 
import bmesh
import bpy
import copy

class Particle:

    def __init__(self, position, direction):
        
        self.position = np.array(position)
        self.direction = np.array(direction) / np.linalg.norm(np.array(direction)) # normalised
        #self.n1 = None
        #self.n2 = None

    def move(self, amp):

        self.position += self.direction * np.array(amp)


    """
    def interpolate_additional_neigh(self, i_neigh, n_interpolated):

        neigh = None

        if i_neigh == 1:
            neigh = self.n1

        else:
            neigh = self.n2

        delta = 1 / n_interpolated
        t = delta

        interpolated = []
        center = np.array([0,0,0])

        for i in range(n_interpolated):

            position = self.position + (1-t) * neigh.position
            direction = position - center

            interpolated.append(Particle(position, direction))

        if i_neigh == 1:
            self.n1 = interpolated[0]

        

    
    def check_neigh_dist(self, max_dist, center):

        added_n1 = []
        added_n2 = []

        if np.linalg.norm(self.position - self.n1.position) > max_dist:
            
            added_n1 = self.interpolate_additional_neigh(1, center)

        if np.linalg.norm(self.position - self.n2.position) > max_dist:

            added_n2 = self.interpolate_additional_neigh()


    """






class Border:

    def __init__(
        self,
        n_ini_particles,
        r_ini,
        center,
        max_dist,
        move_amp
        ):

        self.n_ini_particles = n_ini_particles
        self.r_ini = r_ini
        self.center = center 
        self.max_dist = max_dist
        self.move_amp = move_amp
        self.particles = self.__init_particles__()


    def __init_particles__(self):

        segment = 2 * np.pi / self.n_ini_particles
        phi = 0
        particles = []

        # create particles on circle

        for i in range(self.n_ini_particles):

            x = self.r_ini * np.cos(phi)
            y = self.r_ini * np.sin(phi)
            z = 0

            dx = x - self.center[0]
            dy = y - self.center[1]
            dz = 0

            particles.append(Particle([x,y,z], [dx, dy, dz]))

            phi += segment

        """
        # add neighbours to particles
        edges = []
        for i in range(self.n_ini_particles):

            if i == self.n_ini_particles - 1:

                edge = [particles[i-1], particles[i], particles[0]]

            edge = [particles[i-1], particles[i], particles[i+1]]

            
            if i == self.n_ini_particles - 1:

                particles[i].n1 = particles[i-1]
                particles[i].n2 = particles[0]

            particles[i].n1 = particles[i-1]
            particles[i].n2 = particles[i+1]
            


        return edges

        """

        return particles


    # nb idx1 < idx2
    def interpolate(self, idx1, idx2, n_interpolated):

        p1 = self.particles[idx1]
        p2 = self.particles[idx2]

        delta = 1 / n_interpolated
        t = 0

        particles = []

        for i in range(n_interpolated-1):

            t += delta

            position = (1-t) * p1.position + t * p2.position
            direction = position - self.center

            particles.append(Particle(position, direction))

            

        print("interpolated", p1.position, p2.position)
        for i in particles:
            print(i.position)


        return particles

    

    def grow_particle(self, particle_idx):

        extended_particles = copy.copy(self.particles)

        particle = self.particles[particle_idx]
        l_particle = self.particles[particle_idx-1]
        r_particle = None
        r_idx = None

        if particle_idx == len(self.particles) - 1:
            r_particle = self.particles[0]
            r_idx = 0
        else:
            r_particle = self.particles[particle_idx + 1]
            r_idx = particle_idx + 1


        # move chosen particle
        particle.move(self.move_amp)
        new_particles = []
        added = 0

        # interpolate 
        if np.linalg.norm(l_particle.position - particle.position) > self.max_dist:

        

            new_particles = self.interpolate(particle_idx-1, particle_idx, 3)

            insert_idx = particle_idx
            if particle_idx-1 < 0:
                insert_idx = len(extended_particles)

            for new_p in new_particles:

                extended_particles.insert(insert_idx, new_p)
                insert_idx += 1

        

            added = len(new_particles)

        if np.linalg.norm(particle.position - r_particle.position) > self.max_dist:

            
            new_particles = self.interpolate(particle_idx, r_idx, 3)

            insert_idx = particle_idx + 1 + added

            for new_p in new_particles:

                extended_particles.insert(insert_idx, new_p)
                insert_idx += 1

            

        return extended_particles

    def construct_mesh(self, particles, id):

        bm = bmesh.new()

        for particle in particles:
            bm.verts.new(particle.position)

        bm.faces.new(bm.verts)

        # add a new mesh data
        layer_mesh_data = bpy.data.meshes.new(str(id)+"_data")  

        # add a new empty mesh object using the mesh data
        layer_mesh_object = bpy.data.objects.new(str(id)+"_object", layer_mesh_data) 

        # make the bmesh the object's mesh
        # transfer bmesh data do mesh data which is connected to empty mesh object
        bm.to_mesh(layer_mesh_data)
        bm.free()

        # add to scene
        bpy.context.scene.objects.link(layer_mesh_object)
    
    def grow_rand(self, n_iter):

        for i in range(n_iter):

            particle_idx = np.random.choice(len(self.particles)-1, 1)[0]

            self.particles = self.grow_particle(particle_idx)

        self.construct_mesh(self.particles, 1)

            

        


        


m = Border(
        n_ini_particles=10,
        r_ini=0.2,
        center=[0,0,0],
        max_dist=0.5,
        move_amp=0.2
)

m.grow_rand(30)






    
