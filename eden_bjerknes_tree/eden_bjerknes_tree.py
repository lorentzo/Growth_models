import numpy as np
import time 
import matplotlib.pyplot as plt

def find_grow_sites(plate, populated):

    found_grow_sites = []
    found_potential_sites = []

    "check around populated cells"
    for pop in populated:

            i = pop[0]
            j = pop[1]

            if plate[i, j+1] == 0:
                found_potential_sites.append((i, j+1))

            if plate[i, j-1] == 0:
                found_potential_sites.append((i, j-1))

            if plate[i-1, j] == 0:
                found_potential_sites.append((i-1, j))

            if plate[i+1, j] == 0:
                found_potential_sites.append((i+1, j))

    "take ones with only one neighbour"
    for potential in found_potential_sites:

        k = potential[0]
        l = potential[1]

        n_neigh = 0

        if plate[k, l+1] == 1:
            n_neigh += 1

        if plate[k, l-1] == 1:
            n_neigh += 1

        if plate[k-1, l] == 1:
            n_neigh += 1

        if plate[k+1, l] == 1:
            n_neigh += 1

        if n_neigh <= 1:

            found_grow_sites.append(potential)

    return found_grow_sites

                
def main():
  
    "initial conditions"
    plate = np.zeros((500,500))
    n_iter = 10000
    populated = [(250,250)]

    "occupy cells according to ini cond"
    for pop in populated:
        plate[pop[0], pop[1]] = 1

    "start growth"
    cnt_iter = 0
    while cnt_iter < n_iter:

        "Returns coordinates where next cell could be generated: [(x1,y1),...]"
        grow_sites = find_grow_sites(plate, populated)
        
        "choose one grow site at random"
        next_grow_site_idx = np.random.randint(low=0, high=len(grow_sites), size=1)[0]
        next_grow_site_coord = grow_sites[next_grow_site_idx]

        "occupy chosen grow site"
        populated.append(next_grow_site_coord)
        plate[next_grow_site_coord[0], next_grow_site_coord[1]] = 1

        cnt_iter = cnt_iter + 1

    plt.imshow(plate)
    plt.show()


main()