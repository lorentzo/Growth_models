import numpy as np 
import copy
import math
import bpy


class Branch():

    def __init__(self, position, parent, direction):
        self.position = position
        self.parent = parent
        self.direction = direction
        self.count = 0

        self.original_direction = copy.copy(direction)

    def reset(self):
            self.direction = copy.copy(self.original_direction)
            self.count = 0

    def give_next_branch(self):

        next_position = np.array(self.position) + np.array(self.direction)
        next_branch = Branch(next_position, self, copy.copy(self.direction))
        return next_branch

    def show(self, mball):

        n_samples = 1
        delta_t = 1 / n_samples

        if self.parent != None:

            t = 0
            for sample in range(n_samples):

                pos = (1-t) * np.array(self.parent.position) + t * np.array(self.position)

                #bpy.ops.mesh.primitive_uv_sphere_add(location=pos, size=0.4, segments=5)
                element = mball.elements.new()
                element.co = pos
                element.radius = 1.0

                t += delta_t





class Leaf():

    def __init__(self):
        self.position = np.random.rand(3) * 70 - 35
        self.position[2] = np.random.rand(1)[0]*5
        self.reached = False

    def show(self):
        bpy.ops.mesh.primitive_cube_add(location=self.position, radius=0.3)


class Tree():

    def __init__(self, root_position, id):

        self.n_leaves = 150
        self.root_position = root_position
        self.id = id
        
        self.max_dist = 5
        self.min_dist = 2
        
        self.leaves = []
        
        self.branches = []

        for i in range(self.n_leaves):
            self.leaves.append(Leaf())

        # create root of the tree (point without parent) and turn its direction to leafs
        self.root = Branch(self.root_position, None, None)
        closest_leaf_to_root = self.find_closest_leaf_to_branch(self.root)
        root_direction = np.array(closest_leaf_to_root.position) - np.array(self.root.position)
        root_direction /= np.linalg.norm(root_direction)
        self.root.direction = root_direction

        # add root to branches
        self.branches.append(self.root)


    def find_closest_leaf_to_branch(self, branch):

        # random ini
        closest_dist = math.inf
        closest_leaf = self.leaves[0]

        for leaf in self.leaves:

            dist = np.linalg.norm(np.array(leaf.position)-np.array(branch.position))

            if dist < closest_dist:
                closest_dist = dist
                closest_leaf = leaf

        return closest_leaf


    def grow_to_point_cloud(self):

        # grow the branch to point cloud
        curr_branch = self.root 
        found = False

        while not found:

            for i in range(self.n_leaves):

                dist = np.linalg.norm(np.array(self.leaves[i].position)-np.array(curr_branch.position))

                if dist < self.max_dist:
                    found = True

            # create a new branch
            if not found:

                branch = curr_branch.give_next_branch()
                curr_branch = branch
                self.branches.append(curr_branch)

    def grow_through_point_cloud(self):

        n_reached = 0

        while n_reached < self.n_leaves:

            # grow
            for leaf in self.leaves:

                if leaf.reached == True:
                    continue

                closest_branch = None
                record = math.inf

                for branch in self.branches:

                    dist = np.linalg.norm(np.array(leaf.position) - np.array(branch.position))

                    if dist < self.min_dist:

                        leaf.riched = True
                        n_reached += 1
                        closest_branch = None
                        break

                    elif closest_branch == None or dist < record:
                        closest_branch = branch
                        record = dist

                if closest_branch != None:

                    new_direction = np.array(leaf.position) - np.array(closest_branch.position)
                    new_direction = new_direction / np.linalg.norm(new_direction)
                    closest_branch.direction = new_direction
                    closest_branch.count += 1 


                # grow branches according to number of times extended
                for branch in self.branches:
                    if branch.count > 0:
                        branch.direction /= branch.count

                        new_position = branch.position + branch.direction
                        new_branch = Branch(new_position, branch, copy.copy(branch.direction))

                        self.branches.append(new_branch) 

                    branch.reset()

    def show_branches(self, cnt):

        scene = bpy.context.scene
        # add metaball object
        mball = bpy.data.metaballs.new("MetaBall")
        obj = bpy.data.objects.new("MetaBallObject", mball)
        scene.objects.link(obj)

        print(len(self.branches))

        sample = 0
        
        for branch in self.branches:

            sample += 1
            

            branch.show(mball)

            if sample % 50 == 0:
                cnt[0] += 1
                bpy.context.scene.render.filepath = '/home/lovro/Documents/FER/diplomski/Growth_models/blender_implementations/cetvrti/izlazi/'+str(cnt[0])
                bpy.ops.render.render(write_still=True)

    def show_leaves(self):

        for leaf in self.leaves:

            leaf.show()


def main():

    obj_camera = bpy.data.objects["Camera"].location[0] = 0
    obj_camera = bpy.data.objects["Camera"].location[1] = 0
    obj_camera = bpy.data.objects["Camera"].location[2] = 100
    
    obj_camera = bpy.data.objects["Camera"].rotation_euler[0] = 0
    obj_camera = bpy.data.objects["Camera"].rotation_euler[1] = 0
    obj_camera = bpy.data.objects["Camera"].rotation_euler[2] = 0

    cnt = [0]

    tree1 = Tree([-10,-10,-10],1)

    tree1.grow_to_point_cloud()
    
    tree1.grow_through_point_cloud()
    
    tree1.show_branches(cnt)
    
    
    tree2 = Tree([50,50,50],2)
    
    tree2.grow_to_point_cloud()
    
    tree2.grow_through_point_cloud()
    
    tree2.show_branches(cnt)
    
    
    tree3 = Tree([-50,50,50],3)
    
    tree3.grow_to_point_cloud()
    
    tree3.grow_through_point_cloud()
    
    tree3.show_branches(cnt)
    

main()


