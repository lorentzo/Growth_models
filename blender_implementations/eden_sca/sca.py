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

        # if distance between parent and current branch is large use interpolation
        delta_t = 1 / n_samples

        if self.parent != None:

            t = 0
            for sample in range(n_samples):

                # add new metamesh element
                "(1-t) * np.array(self.parent.position) + t *"
                pos = np.array(self.position)
                element = mball.elements.new()
                element.co = pos
                element.radius = 1.0

                # alternatively add sphere mesh instead of metamesh
                #bpy.ops.mesh.primitive_uv_sphere_add(location=pos, size=0.4, segments=5)

                t += delta_t

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
class SCA():

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
    perform growth:
        + from root till leaves cloud
        + trough leaves cloud
    ********************************************************************* """
    def grow(self):

        self.grow_to_point_cloud()
        self.grow_through_point_cloud()

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
    def show_branches(self, metamesh, iter):

        branch = self.branches[iter]
        branch.show(metamesh, 1)

    """ *********************************************************************
    PUBLIC HELPER FUNCTION
    Using blender mesh display all leaves
    ********************************************************************* """
    def show_leaves(self):
        for leaf in self.leaves:
            leaf.show(0.3)
