import numpy as np 
import bpy
import os

class Particle:

    def __init__(self, position, size):

        self.position = np.array(position)
        self.size = size

        bpy.ops.mesh.primitive_uv_sphere_add(size=size, location=position)
        self.blender_sphere = bpy.context.object

    
class FlowAgg:

    """ #####################################################################
        area: {xm:float, xM:float, ym:float, yM:float}
        jump_amp: {x:float, y:float}
    ##################################################################### """

    def __init__(
        self, 
        n_particles, 
        jump_amp,
        area,
        particle_size,
        prox_thresh,
        render_out
    ):

        self.n_particles = n_particles
        self.jump_amp = jump_amp
        self.area = area
        self.particle_size = particle_size
        self.prox_thresh = prox_thresh
        self.render_out = render_out

        self.aggregate = []
        self.x0 = (area["xM"] - area["xm"]) / 2 + area["xm"]
        self.y0 = (area["yM"] - area["ym"]) / 2 + area["ym"]
        self.aggregate.append(Particle([self.x0, self.y0, 0], particle_size))


    def ini_particle(self):

        r = np.random.rand()

        # bottom spawn
        if r < 0.25:
            x = np.random.rand() * (self.area["xM"] - self.area["xm"]) + self.area["xm"]
            return Particle([x, self.area["ym"], 0], self.particle_size)

        # top spawn
        if r > 0.25 and r < 0.5:
            x = np.random.rand() * (self.area["xM"] - self.area["xm"]) + self.area["xm"]
            return Particle([x, self.area["yM"], 0], self.particle_size)

        # left spawn
        if r > 0.5 and r < 0.75:
            y = np.random.rand() * (self.area["yM"] - self.area["ym"]) + self.area["ym"]
            return Particle([self.area["xm"], y, 0], self.particle_size)

        # right spawn
        if r > 0.75:
            y = np.random.rand() * (self.area["yM"] - self.area["ym"]) + self.area["ym"]
            return Particle([self.area["xM"], y, 0], self.particle_size)


    def move_angle(self, phi_low, phi_high, particle):

        phi = np.random.rand() * (phi_high - phi_low) + phi_low

        dx = np.cos(phi)
        dy = np.sin(phi)

        particle.position[0] += self.jump_amp["x"] * dx
        particle.position[1] += self.jump_amp["y"] * dy

        particle.blender_sphere.location = particle.position

    def move(self, particle):

        # middle bottom
        if particle.position[0] > self.x0 - 1 and particle.position[0] < self.x0 + 1 and particle.position[1] < self.y0:

            self.move_angle(0, np.pi, particle)

        # middle top
        if particle.position[0] > self.x0 - 1 and particle.position[0] < self.x0 + 1 and particle.position[1] > self.y0:

            self.move_angle(np.pi, 2 * np.pi, particle)

        
        # middle left
        if particle.position[1] > self.y0 - 1 and particle.position[1] < self.y0 + 1 and particle.position[0] < self.x0:

            self.move_angle(- np.pi / 2, np.pi / 2, particle)

        # middle right
        if particle.position[1] > self.y0 - 1 and particle.position[1] < self.y0 + 1 and particle.position[0] > self.x0:

            self.move_angle(np.pi / 2, 3 * np.pi /2, particle)


        # top left
        if particle.position[0] < self.x0 and particle.position[1] > self.y0:

            self.move_angle(3 * np.pi / 2, 2 * np.pi, particle)
            
        # top right
        if particle.position[0] > self.x0 and particle.position[1] > self.y0:

            self.move_angle(np.pi, 3 * np.pi / 2, particle)

        # bot left
        if particle.position[0] < self.x0 and particle.position[1] < self.y0:

            self.move_angle(0, np.pi / 2, particle)

        # bot right
        if particle.position[0] > self.x0 and particle.position[1] < self.y0:

            self.move_angle(np.pi / 2, np.pi, particle)


    def close(self, particle):

        for a_particle in self.aggregate:

            if np.linalg.norm(a_particle.position - particle.position) < self.prox_thresh:

                return True

            

        return False


    def planar_force(self):

        sum_planar = 0
        for a_particle in self.aggregate:
            sum_planar += a_particle.position

        return sum_planar / len(self.aggregate)

    def spring_force(self, particle):

        sum_spring = 0
        for a_particle in self.aggregate:
            dist = particle.position - a_particle.position
            dist_norm = dist / np.linalg.norm(dist)
            sum_spring += a_particle.position + 1.3 * dist_norm

        return  sum_spring / len(self.aggregate) 

    def grow(self):

        render_iter = 0

        for i_particle in range(self.n_particles):

            particle = self.ini_particle()

            while True:

                self.move(particle)

                if self.close(particle) == True:

                    # stick particle to aggregate
                    self.aggregate.append(particle)
    
                    # and planar and spring force
                    planar_target = self.planar_force()

                    for a_particle in self.aggregate:

                        spring_target = self.spring_force(a_particle)

                        a_particle.position += 1.2 * (spring_target - a_particle.position) + 1.2 * (planar_target - a_particle.position) 
                        
                        a_particle.blender_sphere.location = a_particle.position

                
                    # render
                    bpy.context.scene.render.filepath = os.path.join(self.render_out, str(render_iter))
                    bpy.ops.render.render(write_still=True)
                    render_iter += 1

                    break

                
                

def main():

    fa = FlowAgg(n_particles=100,
                jump_amp={"x":0.2, "y":0.2},
                area={"xm":-5, "xM":5, "ym":-5, "yM":5},
                particle_size=0.2,
                prox_thresh=0.4,
                render_out='/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/flow_agg/tmp/'
                )

    fa.grow()
    
main()
