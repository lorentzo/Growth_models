
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

import numpy as np 
import bpy
import os

class Particle:

    def __init__(self, position, size):

        self.position = np.array(position)
        self.size = size
        self.stuck = False

        bpy.ops.mesh.primitive_uv_sphere_add(size=size, location=position)
        self.blender_sphere = bpy.context.object

    
class FlowAgg:

    """ #####################################################################
        area: {xm:float, xM:float, ym:float, yM:float}
        area: {xm:float, ym: float, radius:float}
        jump_amp: {x:float, y:float}
    ##################################################################### """

    def __init__(
        self, 
        radius_range,
        jump_amp,
        area,
        particle_size,
        prox_thresh,
        render_out
    ):

        self.radius_range = radius_range
        self.jump_amp = jump_amp
        self.area = area
        self.particle_size = particle_size
        self.prox_thresh = prox_thresh
        self.render_out = render_out

        self.aggregate = []
        self.x0 = area["xm"]
        self.y0 = area["ym"]
        self.aggregate.append(Particle([self.x0, self.y0, 0], particle_size))


    def ini_particle(self):

        phi = np.random.rand() * 2 * np.pi
        x = self.area["radius"] * np.cos(phi)
        y = self.area["radius"] * np.sin(phi)

        return Particle([x,y,0], self.particle_size)


    def move_angle(self, phi_low, phi_high, particle, add_amp=1):

        phi = np.random.rand() * (phi_high - phi_low) + phi_low

        dx = np.cos(phi)
        dy = np.sin(phi)

        particle.position[0] += self.jump_amp["x"] * add_amp * dx
        particle.position[1] += self.jump_amp["y"] * add_amp * dy

        particle.blender_sphere.location = particle.position

    def move(self, particle):

        # if close to center

        # middle bottom
        if particle.position[0] > self.x0 - 1 and particle.position[0] < self.x0 + 1 and particle.position[1] < self.y0:

            self.move_angle(np.pi, 3*np.pi/2, particle, 4)

        # middle top
        if particle.position[0] > self.x0 - 1 and particle.position[0] < self.x0 + 1 and particle.position[1] > self.y0:

            self.move_angle(- np.pi / 2, np.pi / 2, particle, 4)

        
        # middle left
        if particle.position[1] > self.y0 - 1 and particle.position[1] < self.y0 + 1 and particle.position[0] < self.x0:

            self.move_angle(0, np.pi, particle, 4)

        # middle right
        if particle.position[1] > self.y0 - 1 and particle.position[1] < self.y0 + 1 and particle.position[0] > self.x0:

            self.move_angle(np.pi, 2 * np.pi, particle, 4)


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


    def is_close(self, particle):

        for a_particle in self.aggregate:

            if np.linalg.norm(a_particle.position - particle.position) < self.prox_thresh:

                return True

        return False


    def add_shape(self, radius, n_particles):

        phis = np.linspace(start=0,
                           stop=2 * np.pi,
                           num=n_particles)

        for phi in phis:

            x = radius * np.cos(phi)
            y = radius * np.sin(phi)
            self.aggregate.append(Particle([x,y,0], self.particle_size))




    def grow(self):

        render_iter = 0
        n_stuck = 0

        radii = np.linspace(start=self.radius_range[0], 
                            stop=self.radius_range[1], 
                            num=self.radius_range[2])

        for radius in radii:

            err = 0.001
            th = np.arccos(2 * np.power((1 - err / radius), 2) - 1)
            n_particles = int(np.ceil(2 * np.pi / th))

            self.add_shape(radius, n_particles)

            free_particles = []
            n_stuck = 0
            for particle in range(n_particles):
                free_particles.append(self.ini_particle())
                
            to_add = []

            while True:

                for f_particle in free_particles:

                    if f_particle.stuck == False:

                        self.move(f_particle)

                        if self.is_close(f_particle) == True:

                            # stick particle to aggregate
                            to_add.append(f_particle)

                            # set stuck
                            f_particle.stuck = True
                            n_stuck += 1

                            # render
                            bpy.context.scene.render.filepath = os.path.join(self.render_out, str(render_iter))
                            bpy.ops.render.render(write_still=True)
                            render_iter += 1

                if n_stuck == len(free_particles):
                    break

            self.aggregate.extend(to_add)


def main():

    fa = FlowAgg(radius_range=[1, 10, 20],
                jump_amp={"x":0.2, "y":0.2},
                area={"xm":0, "ym":0, "radius":10},
                particle_size=0.2,
                prox_thresh=0.4,
                render_out='/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/flow_agg/tmp/'
                )

    fa.grow()
    
main()
