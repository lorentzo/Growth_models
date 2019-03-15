import numpy as np
import time 
import matplotlib.pyplot as plt

def find_grow_sites(plate, populated):

    found_grow_sites = []

    "check around populated cells"
    for pop in populated:

            i = pop[0]
            j = pop[1]

            "if stumpled upon occupied place look for 8 neigh and find free cells"
            if plate[i,j] == 1:

                if plate[i+1, j+1] == 0:
                    found_grow_sites.append((i+1, j+1))

                if plate[i+1, j-1] == 0:
                    found_grow_sites.append((i+1, j-1))

                if plate[i-1, j+1] == 0:
                    found_grow_sites.append((i-1, j+1))

                if plate[i-1, j-1] == 0:
                    found_grow_sites.append((i-1, j-1))

                if plate[i, j+1] == 0:
                    found_grow_sites.append((i, j+1))

                if plate[i, j-1] == 0:
                    found_grow_sites.append((i, j-1))

                if plate[i-1, j] == 0:
                    found_grow_sites.append((i-1, j))

                if plate[i-1, j] == 0:
                    found_grow_sites.append((i-1, j))

    "remove duplicates!"
    return found_grow_sites

                
def main():
  
  plate = np.zeros((1000,1000))
  n_iter = 4000
  populated = [(300,300), (700, 700)]

  for pop in populated:
      plate[pop[0], pop[1]] = 1

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