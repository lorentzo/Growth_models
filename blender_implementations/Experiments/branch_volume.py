import bpy
import bmesh

verts = [[(0, 0, 0), (1, 1, 1)],
         [(1,1,1), (0,2,0)],
         [(0,0,0), (0, -2, 0)]]

def create_mesh(name):

    # mesh data
    mesh_data = bpy.data.meshes.new(name)
    # mesh obj
    mesh_obj = bpy.data.objects.new(name, mesh_data)
    # get scene
    scene = bpy.context.scene
    # link object to scene
    scene.objects.link(mesh_obj)
    # active and select mesh object
    scene.objects.active = mesh_obj
    mesh_obj.select = True
    # select 
    mesh = bpy.context.object.data

    return mesh


def create_bevel_obj(name):

    # create bevel curve
    bpy.ops.curve.primitive_bezier_circle_add()
    circle = bpy.context.active_object 
    circle.name = 'krug'
    circle.scale = (0.05, 0.05, 1)


def mesh_to_curve(mesh_name):  

    obj = bpy.data.objects[mesh_name]
    scene = bpy.context.scene
    scene.objects.active = obj

    # enter object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # transfrom mesh to curve
    bpy.ops.object.convert(target='CURVE')

    create_bevel_obj('krug')

    # bevel options
    bpy.data.curves[mesh_name].fill_mode = 'FULL'
    bpy.data.curves[mesh_name].bevel_object = bpy.data.objects['krug']
    bpy.data.curves[mesh_name].bevel_depth = 0.1


# create empty mesh
mesh = create_mesh('mesh')

# create empy bmesh
bm = bmesh.new()

for pair in verts:

    v1 = pair[0]
    v2 = pair[1]

    #   add points (must be in object mode)
    bpy.ops.object.mode_set(mode='OBJECT')  
    bm.verts.new(v1)  # add a new vert
    bm.verts.new(v2)


#   convert bmesh to mesh
bm.to_mesh(mesh)  

idx1 = 0
idx2 = 1


for pair in verts:

    #print(idx1, idx2)

    # select last two points
    obj = bpy.data.objects['mesh']
    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj.data.vertices[idx1].select = True
    obj.data.vertices[idx2].select = True
    #print(obj.data.vertices[idx1].co, obj.data.vertices[idx2].co)
    bpy.ops.object.mode_set(mode = 'EDIT') 

    # add edge between
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode = 'OBJECT')

    idx1 += 2
    idx2 += 2

mesh_to_curve('mesh')

"""
TESTNI ISPIS VRHOVA U MESHU
obj = bpy.data.objects['mesh']
bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')
for ver in obj.data.vertices:
    print(ver.co)
"""





"""
STVARANJE SPLINEA

coords = [[1,1,1], [3,3,3]]

# curve datablock
curve_data = bpy.data.curves.new('my_curve', type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 2

# map coordinates to spline
polyline = curve_data.splines.new('BEZIER')
polyline.points.add(len(coords))
for i in range(len(coords)):
    x,y,z = coords[i]
    polyline.points[i].co = (x,y,z,1)

# create object
curve_obj = bpy.data.objects.new('my_curve', curve_data)

# attach to scene, make active and select
scene = bpy.context.scene
scene.objects.link(curve_obj)
scene.objects.active = curve_obj
curve_obj.select = True


"""

