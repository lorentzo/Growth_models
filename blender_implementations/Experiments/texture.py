import bpy
import numpy as np 

def main():

    bpy.ops.mesh.primitive_cube_add(radius=1)
    cube = bpy.context.object
    cube.name = 'kocka1'
    cube.location = (5,5,5)

    bpy.ops.mesh.primitive_cube_add(radius=2)
    cube = bpy.context.object
    cube.name = 'kocka2'
    bpy.data.objects['kocka2'].location = (0,0,0)





main()