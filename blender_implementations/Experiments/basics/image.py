import bpy

# set pixel
def set_pixel(img, x, y, width, color):

    offset = (x + int(y * width)) * 4

    for i in range(4):
        img.pixels[offset + i] = color[i]

# blank img
img = bpy.data.images.new('rd', width=640, height=480)
pix = [1.0] * (4 * 640 * 480) #RGBA
img.pixels = pix

# in blender go to UV editor (gdje je Scripting, default..)
# Create image and reference it:
emp = bpy.data.images['a']
width = emp.size[0]
height = emp.size[1]
print(width, height)
pix = [1.0] * (4 * width * height) #RGBA
emp.pixels = pix

for i in range(100):
    
    set_pixel(emp, i, i, width, [0.0, 0.0, 0.0, 0.0])
    
set_pixel(emp, 100, 10, width, [0.0, 0.0, 0.0, 0.0])

