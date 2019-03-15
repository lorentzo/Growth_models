import numpy as np
import matplotlib.pyplot as plt
import time

def ini_particle(starter, r_max):

        x = starter[0]
        y = starter[1]

        if np.random.rand() > 0.5:
            x += r_max
        else:
            x -= r_max

        if np.random.rand() > 0.5:
            y += r_max
        else:
            y -= r_max

        x += np.random.randint(-10, 10, 1)[0]
        y += np.random.randint(-10, 10, 1)[0]

        return x,y

    
def close(walker, cluster):


    for cell in cluster:

            if np.linalg.norm(np.array(cell) - np.array(walker)) < 5:

                return cell

    return None


def attach(cell, plate):

    x = cell[0]
    y = cell[1]

    "check 8-neighbourhood and attach to free slot"

    if plate[x-1][y] == 0:
        plate[x-1][y] = 1

    if plate[x+1][y] == 0:
        plate[x+1][y] = 1

    if plate[x][y-1] == 0:
        plate[x][y-1] = 1

    if plate[x][y+1] == 0:
        plate[x][y+1] = 1

    if plate[x+1][y+1] == 0:
        plate[x+1][y+1] = 1

    if plate[x-1][y+1] == 0:
        plate[x-1][y+1] = 1

    if plate[x-1][y-1] == 0:
        plate[x-1][y-1] = 1

    if plate[x+1][y+1] == 0:
        plate[x+1][y+1] = 1


def main():

    plate = np.zeros((250,250))
    n_particles = 1000
    n_steps = 1000

    starter = (125,125)
    r_max = 50

    cluster = []
    cluster.append(starter)

    for n in range(n_particles):

        "randomly inialize particle position on a plane outside of circle of radious $r_max$ around starting cell $starter"
        x,y = ini_particle(starter, r_max)

        plate_mov = np.zeros((250,250))

        "perform random walk and attach if conditions are met"
        plt.ion()
        for s in range(n_steps):

            val = np.random.randint(1, 4) 

            if val == 1: 
                x += 1

            elif val == 2: 
                x -= 1

            elif val == 3: 
                y += 1

            else: 
                y -= 1

            plate_mov[x][y] = 1

            
            plt.figure(figsize=(256,256))   # create a new figure
            plt.plot(plate_mov)  # plot the figure
            plt.draw()
            time.sleep(1)
            plt.close()
            

        

            "check if after step is close to another particle"

            destination = close((x,y), cluster)

            if not destination == None:

                attach(destination, plate)

        

    plt.imshow(plate)
    plt.show()
                        

main()