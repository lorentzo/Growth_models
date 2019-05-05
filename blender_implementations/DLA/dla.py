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
                r_walk_dist):

        self.center_spawn_circle = center_spawn_circle
        self.r_spawn_circle = r_spawn_circle
        self.r_walk_dist = r_walk_dist

        self.position = self.__init_position__()
        self.found = False

    """
    Spawn walker on random position on circle defined by center_spawn_circle
    and r_spawn_circle
    """
    def __init_position__(self):

        density = 100
        samples = np.linspace(0, np.pi * 2, density)
        random_sample_idx = np.random.randint(0, density, 1)[0]
        random_sample = samples[random_sample_idx]

        x = self.center_spawn_circle[0] + self.r_spawn_circle * np.cos(random_sample)
        y = self.center_spawn_circle[1] + self.r_spawn_circle * np.sin(random_sample)
        z = 0

        return np.array([x,y,z])

    """
    random movement
    """
    def walk(self):

        """
        from current position move randomly.
        Next step is random point on circle with current position as
        center and r_walk_dist as radius
        """
        x = self.position[0] + self.r_walk_dist * np.sin(np.random.rand() * np.pi * 2)
        y = self.position[1] + self.r_walk_dist * np.cos(np.random.rand() * np.pi * 2)
        z = 0

        self.position = np.array([x,y,z])

        """
        if walker goes outside of certain radius, reset its position
        as random point on starting circle
        """
        dist = np.linalg.norm(self.center_spawn_circle - self.position)

        if dist > self.r_spawn_circle + 10:
            self.position = self.__init_position__()

class Tree:

    def __init__(self, 
                 radius_spawn,
                 ini_radius,
                 center,
                 stick_dist,
                 n_walkers,
                 walker_walk_dist
                ):

        self.radius_spawn = radius_spawn
        self.ini_radius = ini_radius
        self.center = center
        self.stick_dist = stick_dist
        self.n_walkers = n_walkers
        self.walker_walk_dist = walker_walk_dist


        # create initial walker
        init_walker = Walker(self.center,
                             self.radius_spawn,
                             self.walker_walk_dist)

        init_walker.position = [0,0,0]

        self.tree = []
        #self.tree.append([None, init_walker])
        self.__init_tree__()

    "define where walkers will be stuck"
    def __init_tree__(self):

        sample_density = 20
        circle_samples = np.linspace(0, np.pi * 2, sample_density)

        # NOTE: use noise so circle is bit wavy
        for circle_sample in circle_samples:

            init_walker = Walker(self.center,
                                 self.radius_spawn,
                                 self.walker_walk_dist)

            x = self.center[0] + self.ini_radius * np.cos(circle_sample)
            y = self.center[1] + self.ini_radius * np.sin(circle_sample)
            init_walker.position = np.array([x,y,0])

            self.tree.append([None, init_walker])

    def grow(self):

        walkers_stuck = 0

        walkers = []

        # initialise walkers
        for i in range(0, self.n_walkers):

            walker = Walker(self.center,
                            self.radius_spawn,
                            self.walker_walk_dist)

            walkers.append(walker)

        # perform random walk for every walker until stuck
        while walkers_stuck < self.n_walkers:

            # for every walker
            for walker in walkers:

                # check if current walker is stuck
                if not walker.found:

                    # if not stuck perform random movement and check distance  
                    for walker_tree in self.tree:

                        walker_tree_rel = walker_tree[1]

                        dist = np.linalg.norm(walker.position - walker_tree_rel.position)

                        if dist <= self.stick_dist:
                            print(dist)
                            self.tree.append([walker_tree_rel, walker])
                            walkers_stuck += 1
                            print(walkers_stuck)
                            walker.found = True
                            break

                        else:

                            walker.walk()

        




def main():

    "define and grow dla tree"
    tree = Tree(radius_spawn=6, 
                ini_radius=1, 
                center=np.array([0,0,0]), 
                stick_dist=0.3, 
                n_walkers=100, 
                walker_walk_dist=0.2)
    tree.grow()

    # create bmesh
    bm = bmesh.new()
    for branch in tree.tree:
        if branch[0] == None:
            bm.verts.new(branch[1].position)
            continue
        v1 = bm.verts.new(branch[0].position)
        v2 = bm.verts.new(branch[1].position)
        bm.edges.new((v1, v2))

    # create mesh object using bmesh data
    mesh_data = bpy.data.meshes.new("dla_mesh_data")
    mesh_obj = bpy.data.objects.new("dla_mesh_obj", mesh_data)
    bm.to_mesh(mesh_data)
    bm.free()

    # add mesh object to the scene
    scene = bpy.context.scene
    scene.objects.link(mesh_obj)

        




    """

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

    # create texture 
    texture = bpy.data.textures.new('diplace_tex', type='VORONOI')

    for element in tree.tree:

        element_pos = element.position

        #bm.verts.new(element_pos)
        bpy.ops.mesh.primitive_uv_sphere_add(location=element_pos,
                                            size=radius)
        bpy.context.object.scale = (0.5,0.5,0.5)

        bpy.ops.object.modifier_add(type='DISPLACE')
        
        bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["diplace_tex"]

     
        radius *= shrink

    # make mesh from b mesh
    bm.to_mesh(mesh)   

    bm.free() 
    """

main()