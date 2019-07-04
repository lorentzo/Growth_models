
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

    def __init__(self, position, jump_amp, size):

        self.position = np.array(position)
        self.stuck = False
        self.jump_amp = jump_amp

        bpy.ops.mesh.primitive_uv_sphere_add(size=size, location=position)
        self.blender_sphere = bpy.context.object

    def move(self):
        phi = np.random.rand() * 2 * np.pi
        dx = np.cos(phi)
        dy = np.sin(phi)

        self.position[0] += self.jump_amp * dx
        self.position[1] += self.jump_amp * dy

        self.blender_sphere.location = self.position


class DLA:

    """
    area = {"radius":r, "center":[x,y,z]}
    """
    def __init__(self, area, n_particles, jump_amp, prox_thresh, kill_dist, size):
        self.area = area
        self.n_particles = n_particles
        self.jump_amp = jump_amp
        self.prox_thresh = prox_thresh
        self.size = size
        self.kill_dist = kill_dist

        self.aggregate = []
        self.aggregate.append(Particle(area["center"], jump_amp, size))


    def ini_particle(self):
        phi = np.random.rand() * 2 * np.pi
        x = self.area["center"][0] + self.area["radius"] * np.cos(phi)
        y = self.area["center"][1] + self.area["radius"] * np.sin(phi)
        return Particle([x,y,0], self.jump_amp, self.size)

    def is_close(self, particle):
        for a_particle in self.aggregate:
            if np.linalg.norm(a_particle.position - particle.position) < self.prox_thresh:
                return True
            else:
                return False

    def too_far(self, particle):
        if np.linalg.norm(particle.position - np.array(self.area["center"])) > self.kill_dist:
            return True
        else:
            return False

    def grow(self):

        free_particles = []
        n_stuck = 0
        render_iter = 0
        render_out='/home/lovro/Documents/FER/diplomski/growth_models_results/blender_impl/dla/tmp/'
        for i in range(self.n_particles):
            free_particles.append(self.ini_particle())

        while True:

            for f_particle in free_particles:

                if f_particle.stuck == False:

                    f_particle.move()

                    if self.too_far(f_particle) == True:
                        phi = np.random.rand() * 2 * np.pi
                        x = self.area["center"][0] + self.area["radius"] * np.cos(phi)
                        y = self.area["center"][1] + self.area["radius"] * np.sin(phi)
                        f_particle.position = np.array([x,y,0])

                    if self.is_close(f_particle):

                        self.aggregate.append(f_particle)

                        f_particle.stuck = True

                        n_stuck += 1
                        print(n_stuck)

                    

                    # render
                    bpy.context.scene.render.filepath = os.path.join(render_out, str(render_iter))
                    bpy.ops.render.render(write_still=True)
                    render_iter += 1

            if n_stuck == self.n_particles:
                break



def main():

    print("start")

    dla = DLA(area={"radius":3, "center":[0,0,0]},
                n_particles = 100,
                jump_amp=0.2,
                prox_thresh=0.4,
                kill_dist=5,
                size=0.2)
                
    dla.grow()

                
main()
