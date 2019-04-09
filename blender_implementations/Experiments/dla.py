import bpy
import numpy as np  
import bmesh


class Walker:

    """
    center_spawn_circle: np.array([x, y, z])
    r_spawn_circle: scalar
    r_walk: scalar
    """
    def __init__(self, 
                center_spawn_circle,
                r_spawn_circle, 
                r_walk):

        self.center_spawn_circle = center_spawn_circle
        self.r_spawn_circle = r_spawn_circle
        self.r_walk = r_walk

        self.position = self.__init_position__()
        self.found = False

    def __init_position__(self):

        density = 100
        samples = np.linspace(0, 2 * np.pi, density)
        random_sample_idx = np.random.randint(0, density, 1)[0]
        random_sample = samples[random_sample_idx]

        x = self.center_spawn_circle[0] + self.r_spawn_circle * np.cos(random_sample)
        y = self.center_spawn_circle[1] + self.r_spawn_circle * np.sin(random_sample)
        z = 0

        return np.array([x,y,z])

    def walk(self):

        x = self.position[0] + self.r_walk * np.sin(np.random.rand() * 2 * np.pi)
        y = self.position[1] + self.r_walk * np.cos(np.random.rand() * 2 * np.pi)
        z = 0

        self.position = np.array([x,y,z])

        dist = np.linalg.norm(self.center_spawn_circle - self.position)

        if dist > self.r_spawn_circle + 10:
            self.position = self.__init_position__()

class Tree:

    def __init__(self, 
                 radius_spawn,
                 radius_stick,
                 center,
                 stick_dist,
                 n_walkers,
                 walker_walk_dist
                ):

        self.radius_spawn = radius_spawn
        self.radius_stick = radius_stick
        self.center = center
        self.stick_dist = stick_dist
        self.n_walkers = n_walkers
        self.walker_walk_dist = walker_walk_dist

        self.tree = []
        self.__init_tree__()

    "define where walkers will be stuck"
    def __init_tree__(self):

        sample_density = 20
        circle_samples = np.linspace(0, 2 * np.pi, sample_density)

        # NOTE: use noise so circle is bit wavy
        for circle_sample in circle_samples:

            init_walker = Walker(self.center,
                                 self.radius_spawn,
                                 self.walker_walk_dist)

            x = self.center[0] + self.radius_stick * np.cos(circle_sample)
            y = self.center[1] + self.radius_stick * np.sin(circle_sample)
            init_walker.position = np.array([x,y,0])

            self.tree.append(init_walker)

    def grow(self):

        walkers_stuck = 0

        walkers = []

        for i in range(0, self.n_walkers):

            walker = Walker(self.center,
                            self.radius_spawn,
                            self.walker_walk_dist)

            walkers.append(walker)

        while walkers_stuck < self.n_walkers:

            for walker in walkers:

                if not walker.found:

                    for walker_tree in self.tree:

                        dist = np.linalg.norm(walker.position - walker_tree.position)

                        if dist < self.stick_dist:

                            self.tree.append(walker)
                            walkers_stuck += 1
                            print(walkers_stuck)
                            walker.found = True
                            break

                        else:

                            walker.walk()

        




def main():

    "define and grow dla tree"
    tree = Tree(radius_spawn=100, 
                radius_stick=10, 
                center=np.array([0,0,0]), 
                stick_dist=6, 
                n_walkers=900, 
                walker_walk_dist=1)
    tree.grow()

    "use blender to display"
    # mesh data
    mesh_data = bpy.data.meshes.new("mesh")
    # mesh obj
    mesh_obj = bpy.data.objects.new("geometrija", mesh_data)
    # get scene
    scene = bpy.context.scene
    # link object to scene
    scene.objects.link(mesh_obj)
    # active and select mesh object
    scene.objects.active = mesh_obj
    mesh_obj.select = True
    # select 
    mesh = bpy.context.object.data
    # create b mesh
    bm = bmesh.new()
    
    radius = 2
    shrink = 0.9995

    bpy.ops.object.metaball_add(type='BALL', location=np.array([0,0,0]), radius=radius)
    obj = bpy.context.active_object.data

    for element in tree.tree:

        element_pos = element.position

        #bm.verts.new(element_pos)
        bpy.ops.mesh.primitive_uv_sphere_add(location=element_pos,
                                            size=radius)

        # move metaball in direction of new cell
        #element = obj.elements.new()
        #element.co = element_pos
        #element.radius = radius

        radius *= shrink

    # make mesh from b mesh
    bm.to_mesh(mesh)   

    bm.free() 


main()