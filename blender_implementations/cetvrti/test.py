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

    def show(self):

        n_samples = 2
        delta_t = 1 / n_samples

        if self.parent != None:

            t = 0
            for sample in range(n_samples):

                pos = (1-t) * np.array(self.parent.position) + t * np.array(self.position)

                bpy.ops.mesh.primitive_uv_sphere_add(location=pos, size=0.4, segments=5)

                t += delta_t





class Leaf():

    def __init__(self):
        self.position = np.random.rand(3) * 50
        self.position[2] = np.random.rand(1)[0]*5
        self.reached = False

    def show(self):
        bpy.ops.mesh.primitive_cube_add(location=self.position, radius=0.3)


class Tree():

    def __init__(self):

        self.n_leaves = 150
        
        self.max_dist = 5
        self.min_dist = 2
        
        self.leaves = []
        
        
        self.branches = []

        for i in range(self.n_leaves):
            self.leaves.append(Leaf())


    def grow_to_point_cloud(self):

        # create root of the tree (point without parent)
        root = Branch([-10,-10,-10], None, [0.25,0.25,0.25])

        # add root to branches
        self.branches.append(root)

        # grow the branch to point cloud
        curr_branch = root 
        found = False

        while not found:

            for i in range(self.n_leaves):

                dist = np.linalg.norm(np.array(self.leaves[i].position)-np.array(curr_branch.position))
                print(dist)

                if dist < self.max_dist:
                    found = True

            # create a new branch
            if not found:
                branch = curr_branch.give_next_branch()
                #bpy.ops.mesh.primitive_cube_add(location=branch.position, radius=0.4)
                curr_branch = branch
                self.branches.append(curr_branch)

    def grow_through_point_cloud(self):

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

            #non_reached_leaves = []
            #for leaf in self.leaves:
            #    if leaf.reached == False:
            #        non_reached_leaves.append(leaf)
            #self.leaves = non_reached_leaves

            for branch in self.branches:
                if branch.count > 0:
                    branch.direction /= branch.count

                    new_position = branch.position + branch.direction
                    new_branch = Branch(new_position, branch, copy.copy(branch.direction))

                    self.branches.append(new_branch) 

                branch.reset()

    def show_branches(self):
        
        for branch in self.branches:

            branch.show()

    def show_leaves(self):

        for leaf in self.leaves:

            leaf.show()


def main():

    tree = Tree()
    #tree.show_leaves()
    tree.grow_to_point_cloud()
    
    tree.grow_through_point_cloud()
    
    tree.show_branches()
    

main()


