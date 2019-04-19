import bpy
import numpy as np 

# create dupli object
bpy.ops.mesh.primitive_cube_add(location=(10,10,10))
cube = bpy.context.object

# create object
bpy.ops.mesh.primitive_plane_add(location=(0,0,0))
plane = bpy.context.object

# add particle system
bpy.ops.object.particle_system_add()
ps = plane.particle_systems[0]
particles = ps.particles 
particles_setting = particles.data.settings

particles_setting.count = 10
particles_setting.type = 'HAIR'
particles_setting.dupli_object = cube
particles_setting.render_type = 'OBJECT'
particles_setting.particle_size = 0.01

print(particles_setting.count)
