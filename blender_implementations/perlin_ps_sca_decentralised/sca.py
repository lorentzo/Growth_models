# -*- coding: utf-8 -*-
""" Space colonization algorithm for branching pattern.

This module defines one SCA object.

Contains:
    Branch class
    Leaf class
    SCA class

"""

# Blender imports.
import bpy

# Standard imports.
import numpy as np 
import copy
import math
import os

class Branch:
    """ Defines the branch of SCA tree

    Attributes:
        position (np.array): end vertex of a branch.
        parent (Branch): parent (containing start vertex) of a branch.
        direction (np.array): direction of growth.

    Metods:
        __init__()
        reset()
        give_next_branch()

    """

    def __init__(self, position, parent, direction):

        # User defined.
        self.position = position
        self.parent = parent
        self.direction = direction

        # Additional variables.
        self.count = 0
        self.original_direction = copy.copy(direction)
        
    def reset(self):
        """ Resets direction of growth and number of leaf influenced the direction."""
        self.direction = copy.copy(self.original_direction)
        self.count = 0

    def give_next_branch(self):
        """ Create new branch using direction and position of existing one. """
        next_position = np.array(self.position) + np.array(self.direction)
        next_branch = Branch(next_position, self, copy.copy(self.direction))
        return next_branch

class Leaf:
    """ Defines attractor point in SCA.

    Attributes:
        center (np.array): center of attractor points area
        spread (np.array): spread of attractor points around center

    Methods:
        __init__()

    """

    def __init__(self, center, spread):
        
        # user defined
        self.center = center
        self.spread = spread
        
        # additional variables
        self.position = self.__calculate_leaf_position()
        self.reached = False

    def __calculate_leaf_position(self):
        """ Calculate leaf position based on center and spread. """

        x = np.random.rand(1)[0] * self.spread[0] - self.spread[0] / 2 + self.center[0]
        y = np.random.rand(1)[0] * self.spread[1] - self.spread[1] / 2 + self.center[1]
        z = np.random.rand(1)[0] * self.spread[2] - self.spread[2] / 2 + self.center[2]
    
        return [x,y,z]

class SCA:
    """ Defines a SCA object.

    Attributes:
        root_position (np.array): starting vertex of SCA.
        leaf_cloud_center (np.array): center of attractor points.
        leaf_spread (np.array): spread of attractor points around center.
        n_leaves (int): number of attractor points.
        growth_dist (dict): {'min':min_dist, 'max':max_dist}

    Methods:
        __init__()
        grow()
    
    """

    def __init__(self, 
                root_position,
                leaves_cloud_center,
                leaves_spread,
                n_leaves):

        # User defined.
        self.root_position = root_position
        self.leaf_cloud_center = leaves_cloud_center
        self.leaves_spread = leaves_spread
        self.n_leaves = n_leaves
        self.growth_dist = {"min":0.5,"max":4} # try different parameters
        
        # Additional variables.
        # Leaf cloud.
        self.leaves = []
        for i in range(self.n_leaves):
            self.leaves.append(Leaf(self.leaf_cloud_center, self.leaves_spread))

        # Create root of the tree (point without parent) and turn its direction to leafs.
        self.branches = []
        self.root = Branch(self.root_position, None, None)
        closest_leaf_to_root = self.__find_closest_leaf_to_branch(self.root)
        root_direction = np.array(closest_leaf_to_root.position) - np.array(self.root.position)
        root_direction /= np.linalg.norm(root_direction)
        self.root.direction = root_direction
        self.branches.append(self.root)

    def __find_closest_leaf_to_branch(self, branch):
        """ For given branch (think of branch as point!) find closest leaf. """

        closest_dist = math.inf
        closest_leaf = self.leaves[0]

        for leaf in self.leaves:
            dist = np.linalg.norm(np.array(leaf.position)-np.array(branch.position))
            if dist < closest_dist:
                closest_dist = dist
                closest_leaf = leaf

        return closest_leaf

    def grow(self):
        """ Performs growth from root to all attractor points. """

        self.__grow_to_point_cloud()
        self.__grow_through_point_cloud()

    def __grow_to_point_cloud(self):
        """ Grow branch from root till leaf cloud. """

        curr_branch = self.root 
        found = False

        while not found:

            for i in range(self.n_leaves):

                dist = np.linalg.norm(np.array(self.leaves[i].position)-np.array(curr_branch.position))

                if dist < self.growth_dist['max']:
                    found = True

            # Create a new branch
            if not found:

                branch = curr_branch.give_next_branch()
                curr_branch = branch
                self.branches.append(curr_branch)

    def __grow_through_point_cloud(self):
        """ Grow branches through leaf cloud. """

        # Number of reached leaves.
        n_reached = 0

        # Grow branches as long exist leaves that are not close to branches.
        while n_reached <= self.n_leaves:

            for leaf in self.leaves:

                if leaf.reached == True:
                    continue

                closest_branch = None
                record = math.inf

                # For current leaf try to find closest branch.
                for branch in self.branches:

                    dist = np.linalg.norm(np.array(leaf.position) - np.array(branch.position))

                    # for current branch leaf is too close. Leaf should not be considered.
                    if dist < self.growth_dist['min']:
                        leaf.riched = True
                        n_reached += 1
                        closest_branch = None
                        break

                    # If current branch is closest or no closest branch exists.
                    elif closest_branch == None or dist < record:
                        closest_branch = branch
                        record = dist

                # For found clostest branch change direction to current leaf.
                if closest_branch != None:

                    new_direction = np.array(leaf.position) - np.array(closest_branch.position)
                    new_direction = new_direction / np.linalg.norm(new_direction)
                    closest_branch.direction = new_direction
                    closest_branch.count += 1 


                # Grow branches according to number of times extended.
                for branch in self.branches:

                    # If leaf was influencing the branch add new branch in its direction.
                    if branch.count > 0:

                        branch.direction /= branch.count
                        new_position = branch.position + branch.direction
                        new_branch = Branch(new_position, branch, copy.copy(branch.direction))

                        self.branches.append(new_branch) 

                    branch.reset()