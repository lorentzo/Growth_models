import bpy
import numpy as np 

def create():

    scene = bpy.context.scene

    mball_data = bpy.data.metaballs.new("mball_datablock")
    mball_obj = bpy.data.objects.new("mball_obj", mball_data)

    scene.objects.link(mball_obj)

    mball_data.resolution = 0.25
    mball_obj.layers[0] = False
    mball_obj.layers[1] = True

    ele = mball_data.elements.new(type='CAPSULE')
    ele.co = (0,0,0)
    ele.radius = 0.4
    """
    ele = mball_data.elements.new(type='PLANE')
    ele.co = (1,0,0)
    ele.radius = 1

    ele = mball_data.elements.new(type='PLANE')
    ele.co = (2,0,0)
    ele.radius = 1
    """

create()

