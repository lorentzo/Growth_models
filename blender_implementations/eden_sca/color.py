import bpy

# specify color
r,g,b = (0.9, 0.1, 0.1)

# get material
material = bpy.data.materials.new(name="Material")

for o in bpy.context.selected_objects:
    o.active_material = material
    o.active_material.diffuse_color = (r,g,b)