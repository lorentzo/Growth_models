#############################################################################
# DESCRIPTION:
# Space colonization algorithm for branching pattern
#############################################################################

""" *************************************************************************
IMPORTS
************************************************************************* """

########################### STANDARD IMPORTS ################################
import numpy as np 
import copy
import math
import bpy
import os

""" *************************************************************************
CLASS
Helper class: defining one branch:
    + starting point of branch is position of parent
    + ending point of branch is position
    + direction of growth is direction
************************************************************************* """
class Branch():

    """ **********************************************************************
    CONSTRUCTOR
    ********************************************************************** """
    def __init__(self, position, parent, direction):

        # user defined
        self.position = position
        self.parent = parent
        self.direction = direction

        # additional variables
        self.count = 0
        self.original_direction = copy.copy(direction)

    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    Resets direction of growth and number of leaf influenced the direction
    ****************************************************************** """
    def reset(self):
            self.direction = copy.copy(self.original_direction)
            self.count = 0

    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    Create new branch using direction and position of existing one
    ****************************************************************** """
    def give_next_branch(self):
        next_position = np.array(self.position) + np.array(self.direction)
        next_branch = Branch(next_position, self, copy.copy(self.direction))
        return next_branch

    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    Using Blender metamesh display branch between parent and current branch
    ****************************************************************** """
    def show(self, mball, n_samples):

        # NOTE if distance between parent and current branch is large use interpolation
    
        element = mball.elements.new()
        element.co = self.position
        element.radius = 1.0

        
    """ ******************************************************************
    PUBLIC HELPER FUNCTION
    Using Blender cylinder mesh display branch between parent and current branch
    # alternatively add sphere mesh instead of cylinder
    #bpy.ops.mesh.primitive_uv_sphere_add(location=pos, size=0.4, segments=5)
    ****************************************************************** """
    def show_tubular(self, thickness):

        if self.parent == None:
            return

        dx = self.position[0] - self.parent.position[0]
        dy = self.position[1] - self.parent.position[1]
        dz = self.position[2] - self.parent.position[2]

        dist = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

        bpy.ops.mesh.primitive_cylinder_add(radius=thickness,
                                            depth=dist,
                                            location=(dx/2 + self.position[0],
                                                      dy/2 + self.position[1],
                                                      dz/2 + self.position[2]))
        
        phi = math.atan2(dy, dx)
        theta = math.acos(dz/dist)

        bpy.context.object.rotation_euler[1] = theta
        bpy.context.object.rotation_euler[2] = phi




""" *********************************************************************
CLASS
Defining position of leaf
********************************************************************* """
class Leaf():

    """ *********************************************************************
    CONSTRUCTOR
    ********************************************************************* """
    def __init__(self, spread_xy, spread_z):
        
        # user defined
        # random points for x,y,z
        self.position = np.random.rand(3) * spread_xy - (spread_xy / 2)
        # as we want primary 2D, z coordinate should have smaller spread
        self.position[2] = np.random.rand(1)[0] * spread_z

        # additional variables
        self.reached = False

    """ *********************************************************************
    PUBLIC HELPER FUNCTION
    Using Blender mesh display leaf position
    ********************************************************************* """
    def show(self, radius):
        bpy.ops.mesh.primitive_cube_add(location=self.position, radius=radius)

""" *********************************************************************
CLASS
Defining Tree as branches and leaves
NOTE: distribution of leaves is very important!
********************************************************************* """
class Tree():

    """ *********************************************************************
    CONSTRUCTOR
    ********************************************************************* """
    def __init__(self, 
                n_leaves, 
                root_position, 
                max_dist, 
                min_dist, 
                leaves_xy_spread,
                leaves_z_spread):

        # user defined
        self.n_leaves = n_leaves
        self.root_position = root_position
        self.max_dist = max_dist
        self.min_dist = min_dist
        self.leaves_xy_spread = leaves_xy_spread
        self.leaves_z_spread = leaves_z_spread
        
        # additional variables
        self.leaves = []
        self.branches = []
        for i in range(self.n_leaves):
            self.leaves.append(Leaf(self.leaves_xy_spread, self.leaves_z_spread))

        # create root of the tree (point without parent) and turn its direction to leafs
        self.root = Branch(self.root_position, None, None)
        closest_leaf_to_root = self.find_closest_leaf_to_branch(self.root)
        root_direction = np.array(closest_leaf_to_root.position) - np.array(self.root.position)
        root_direction /= np.linalg.norm(root_direction)
        self.root.direction = root_direction

        # add root to branches
        self.branches.append(self.root)


    """ *********************************************************************
    PRIVATE HELPER FUNCTION
    For given branch (think of branch as point!) find closest leaf
    ********************************************************************* """
    def find_closest_leaf_to_branch(self, branch):

        # random ini
        closest_dist = math.inf
        closest_leaf = self.leaves[0]

        # find closest leaf
        for leaf in self.leaves:
            dist = np.linalg.norm(np.array(leaf.position)-np.array(branch.position))
            if dist < closest_dist:
                closest_dist = dist
                closest_leaf = leaf

        return closest_leaf

    """ *********************************************************************
    PUBLIC FUNCTION
    first grow branch from root till leaf cloud
    ********************************************************************* """
    def grow_to_point_cloud(self):

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

    """ *********************************************************************
    PUBLIC FUNCTION
    When branch is reached the leaf cloud start growing branches in leaf cloud
    ********************************************************************* """
    def grow_through_point_cloud(self):

        # number of reached leaves
        n_reached = 0

        # grow branches as long exist leaves that are not close to branches 
        while n_reached < self.n_leaves:

            # for every leaf
            for leaf in self.leaves:

                # check if it is not reached
                if leaf.reached == True:
                    continue

                closest_branch = None
                record = math.inf

                # try to find closest branch 
                for branch in self.branches:

                    dist = np.linalg.norm(np.array(leaf.position) - np.array(branch.position))

                    # for current branch leaf is too close. Leaf should not be considered
                    if dist < self.min_dist:
                        leaf.riched = True
                        n_reached += 1
                        closest_branch = None
                        break

                    # if current branch is closest or no closest branch exists
                    elif closest_branch == None or dist < record:
                        closest_branch = branch
                        record = dist

                # for found clostest branch change direction to current leaf
                if closest_branch != None:

                    new_direction = np.array(leaf.position) - np.array(closest_branch.position)
                    new_direction = new_direction / np.linalg.norm(new_direction)
                    closest_branch.direction = new_direction
                    closest_branch.count += 1 


                # grow branches according to number of times extended
                for branch in self.branches:

                    # if leaf was influencing the branch add new branch in its direction
                    if branch.count > 0:

                        branch.direction /= branch.count
                        new_position = branch.position + branch.direction
                        new_branch = Branch(new_position, branch, copy.copy(branch.direction))

                        self.branches.append(new_branch) 

                    branch.reset()

    """ *********************************************************************
    PUBLIC HELPER FUNCTION
    Using blender mesh display all branches
    ********************************************************************* """
    def show_branches(self, cnt, iter_render, render_path):

        # get active scene
        scene = bpy.context.scene

        # add metamesh object
        mball = bpy.data.metaballs.new("MetaBall")
        obj = bpy.data.objects.new("MetaBallObject", mball)
        scene.objects.link(obj)

        print("NUMBER OF BRANCHES:", len(self.branches))

        sample = 0
        for branch in self.branches:

            sample += 1

            # add metamesh object in branch direction
            branch.show(mball, 1)

            # add cylinder in branch direction
            #branch.show_tubular(0.1)

            # render
            if sample % iter_render == 0:
                cnt[0] += 1
                bpy.context.scene.render.filepath = os.path.join(render_path, str(cnt[0]))
                #bpy.ops.render.render(write_still=True)

    """ *********************************************************************
    PUBLIC HELPER FUNCTION
    Using blender mesh display all leaves
    ********************************************************************* """
    def show_leaves(self):
        for leaf in self.leaves:
            leaf.show(0.3)


""" *********************************************************************
MAIN
********************************************************************* """
def main():

    # define camera position and orientation
    bpy.data.objects["Camera"].location[0] = 0
    bpy.data.objects["Camera"].location[1] = 0
    bpy.data.objects["Camera"].location[2] = 100
    bpy.data.objects["Camera"].rotation_euler[0] = 0
    bpy.data.objects["Camera"].rotation_euler[1] = 0
    bpy.data.objects["Camera"].rotation_euler[2] = 0

    # render info
    cnt = [0]
    render_path = '/home/lovro/Documents/FER/diplomski/Growth_models/blender_implementations/SCA/izlazi_sca'

    # first tree
    tree1 = Tree(100, [-10,-10,-10], 10, 2, 70, 5)
    tree1.show_leaves()
    tree1.grow_to_point_cloud()
    tree1.grow_through_point_cloud()
    tree1.show_branches(cnt, 50, render_path)
    
    """
    # second tree
    tree2 = Tree(100, [50,50,50], 10, 2, 70, 5)
    tree2.show_leaves()
    tree2.grow_to_point_cloud()
    tree2.grow_through_point_cloud()
    tree2.show_branches(cnt, 50, render_path)
    
    # third tree
    tree3 = Tree(100, [-50,50,50], 10, 2, 70, 5)
    tree3.show_leaves()
    tree3.grow_to_point_cloud()
    tree3.grow_through_point_cloud()
    tree3.show_branches(cnt, 50, render_path)
    """
    
""" ************************************************************************************** 
ROOT
************************************************************************************** """
if __name__ == "__main__":
    main()


