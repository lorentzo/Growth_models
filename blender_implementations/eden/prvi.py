import bpy
import numpy as np


class EDEN:

    """ ******************************************************************************
    CONSTRUCTOR
    plate_size: [x_max, y_max]
    n_iter: scalar
    starters: [[x01, y01], [x02, y02], ....]
    ******************************************************************************* """
    def __init__(self, plate_size, n_iter, starter):

        "User specified variables"
        self.plate_size = plate_size
        self.n_iter = n_iter
        self.starter = starter

        "Additional variables"
        self.plate = np.zeros(self.plate_size)
        self.populated = []
        self.plate[self.starter[0]][self.starter[1]] = 1
        self.populated.append([self.starter[0], self.starter[1]])

        # create mapping to blender
        self.blender_starter = [-self.starter[0],-self.starter[0]]
        self.blender_cube_radius = 0.4
        self.mapper = {}
        for i in range(self.plate_size[0]):
            for j in range(self.plate_size[1]):
                self.mapper[(i,j)] = (self.blender_starter[0] + i, self.blender_starter[1] + j, 0)
        
    

    """ ***************************************************************************
    PRIVATE
    Helper function: finds free slots around populated cells, 4-neigh
    ***************************************************************************** """
    def find_grow_sites(self):

        found_grow_sites = set()

        "check around populated cells"
        for cell in self.populated:

            found = self.give_free_slots(cell)
            
            for cell in found:

                found_grow_sites.add(cell)

        return list(found_grow_sites)

    """ ********************************************************************************
    PUBLIC
    Helper function: find free slot around given cell
    ********************************************************************************* """
    def give_free_slots(self, cell):

        found_grow_sites = set()

        i = cell[0]
        j = cell[1]

        if self.plate[i, j+1] == 0:
            found_grow_sites.add((i, j+1))

        if self.plate[i, j-1] == 0:
            found_grow_sites.add((i, j-1))

        if self.plate[i-1, j] == 0:
            found_grow_sites.add((i-1, j))

        if self.plate[i+1, j] == 0:
            found_grow_sites.add((i+1, j))

        return list(found_grow_sites)


        """ ****************************************************************************
    PRIVATE
    Helper function: filters populated cells with no free neighbours
    ***************************************************************************** """
    def filter_populated(self):

        filtered = []

        for cell in self.populated:

            free_slots = self.give_free_slots(cell)

            if len(free_slots) > 0:

                filtered.append(cell)

        self.populated = filtered



    """ ****************************************************************************
    PUBLIC
    call to grow eden pattern
    **************************************************************************** """
    def grow_pattern(self):
        
        # create starter meatball object
        bpy.ops.object.metaball_add(type='PLANE', location=self.mapper[self.starter[0], self.starter[1]])
        obj = bpy.context.active_object.data

        for sample in range(self.n_iter):

            "find coordinates where next cell can be spawned"
            grow_sites = self.find_grow_sites()

            "among found coordinates choose randomly one"
            next_grow_site_idx = np.random.randint(low=0, high=len(grow_sites), size=1)[0]
            next_grow_site_coord = grow_sites[next_grow_site_idx]

            "occupy chosen cell"
            self.plate[next_grow_site_coord[0]][next_grow_site_coord[1]] = 1
            self.populated.append([next_grow_site_coord[0], next_grow_site_coord[1]])
     
            element = obj.elements.new()
            element.co = self.mapper[(next_grow_site_coord[0], next_grow_site_coord[1])]
            element.radius = 2

            "filter out cells in populated list with no free slots"
            self.filter_populated()
            
            if sample % 50 == 0:
            
                bpy.context.scene.render.filepath = '/home/lovro/Documents/blender/cetvrti/izlazi/'+str(sample)
                bpy.ops.render.render(write_still=True)


        


"main"
def main():
    
    obj_camera = bpy.data.objects["Camera"].location[0] = 0
    obj_camera = bpy.data.objects["Camera"].location[1] = 0
    obj_camera = bpy.data.objects["Camera"].location[2] = 100
    
    obj_camera = bpy.data.objects["Camera"].rotation_euler[0] = 0
    obj_camera = bpy.data.objects["Camera"].rotation_euler[1] = 0
    obj_camera = bpy.data.objects["Camera"].rotation_euler[2] = 0

    eden = EDEN([100,100], 2000, [50,50])
    eden.grow_pattern()
    
main()