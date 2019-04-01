import bpy
import numpy as np

# get current mode 
curr_mode = bpy.context.object.mode 
print("CURR MODE:", curr_mode)

# set object mode if not
if curr_mode == 'EDIT':
    bpy.ops.object.mode_set(mode='OBJECT')
    curr_mode = bpy.context.object.mode 
    print("Setting OBJECT mode")

# select object    
obj = bpy.data.objects['Mball.001']
print("SElecting mball.001")
print("vertices:", obj.data.vertices[0].co)

# print selected
print('SELECTED:',bpy.context.selected_objects)

# set edit mode if not 
if curr_mode == 'OBJECT':
    bpy.ops.object.mode_set(mode='EDIT')
    curr_mode = bpy.context.object.mode 
    print("setting EDIT mode")
    
# set selection mode
bpy.ops.mesh.select_mode(type='VERT')
print('setting vertices selection mode')

# invert selected vertices
#bpy.ops.mesh.select_all(action='INVERT')

# select vertices around center for certain radius

# diselect all vertices
bpy.ops.mesh.select_all(action='DESELECT')

if curr_mode == 'EDIT':
    bpy.ops.object.mode_set(mode='OBJECT') # for selection object mode should be selected
    curr_mode = bpy.context.object.mode 
    print("Setting OBJECT mode")
    
radius = 10
center = [0,0,0]
for vertex in obj.data.vertices:
    dist = np.linalg.norm(np.array(vertex.co) - np.array(center))
    if dist < radius:
        vertex.select = True
    
# BACK TO EDIT MODE
if curr_mode == 'OBJECT':
    bpy.ops.object.mode_set(mode='EDIT')
    curr_mode = bpy.context.object.mode 
    print("setting EDIT mode")
    
# INVERT SELECTION
bpy.ops.mesh.select_all(action='INVERT')

