
""" ****************************************************************************
IMPORTS
**************************************************************************** """

############################## STANDARD LIBRARIES ##############################
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import argparse

############################## USER LIBRARIES ##################################
from eden_lattice import EDEN
from dla_lattice import DLA
from img_to_video import images_to_video

""" ****************************************************************************
CLASS
EDEN and DLA pattern formation on same plate
Colors agreement: 
    + EDEN: plate: 0, cells: 1
    + DLA: plate: 0, cells: 2, test: 3
**************************************************************************** """
class DLA_EDEN:

    """ ***********************************************************************************
    CONSTRUCTOR
    plate_size: [x_max, y_max]
    n_iter: scalar
    starter: [x,y]
    dla_attractor: 'circle', 'line', 'none'
    radius_spawn, radius_kill, radius_jump: scalars
    NOTE: radius_jump > radius spawn, radius_kill > radius_jump
    NOTE: if not 'eden' or 'dla' in variable name then it is common for both eden and dla
    *********************************************************************************** """
    def __init__(self, 
                 plate_size, 
                 eden_n_iter,
                 dla_n_iter, 
                 starter, 
                 dla_attractor,
                 dla_radius_spawn, 
                 dla_radius_kill, 
                 dla_radius_jump,
                 checkpoint,
                 out_folder):

                 # user specified variables
                 self.plate_size = plate_size
                 self.dla_n_iter = dla_n_iter
                 self.eden_n_iter = eden_n_iter
                 self.starter = starter
                 self.dla_attractor = dla_attractor
                 self.dla_radius_jump = dla_radius_jump
                 self.dla_radius_kill = dla_radius_kill
                 self.dla_radius_spawn = dla_radius_spawn
                 self.checkpoint = checkpoint
                 self.out_folder = out_folder


    """ **************************************************************************************
    PUBLIC
    creates EDEN and DLA pattern on same plate
    ************************************************************************************** """
    def create_pattern(self):

        # initialise EDEN model
        eden = EDEN(self.plate_size, 
                    self.eden_n_iter, 
                    self.starter,
                    self.checkpoint)

        # fill plate with EDEN pattern
        start = time.time()
        eden.grow_pattern()
        end = time.time()
        print("Duration:", end-start)
        eden_plates = eden.give_plates()

        # initialise DLA model
        dla = DLA(self.plate_size, 
                  self.dla_n_iter, 
                  self.starter, 
                  self.dla_attractor,
                  self.dla_radius_spawn, 
                  self.dla_radius_kill,
                  self.dla_radius_jump,
                  self.checkpoint)

        # fill plate with DLA pattern
        start = time.time()
        dla.grow_pattern()
        end = time.time()
        print("Duration:", end-start)
        dla_plates = dla.give_plates()

        # join plates and save to folder
        self.join_and_save(dla_plates, eden_plates)

    """ ***********************************************************************************
    PRIVATE
    Join eden and dla plates 
    save as images in a folder
    *********************************************************************************** """
    def join_and_save(self, dla_plates, eden_plates):

        PATH = os.path.join('.', self.out_folder)
        if not os.path.exists(PATH):
            os.mkdir(PATH)

        n = min(len(eden_plates), len(dla_plates))
        for i in range(n):

            out_file = os.path.join(PATH, str(i+1))

            eden_dla_plate = dla_plates[i] + eden_plates[i]

            fig = plt.figure()
            ax = plt.subplot(111)
            ax.imshow(eden_dla_plate)

            fig.savefig(out_file)


        # create video from images
        img_path = os.path.join('.', self.out_folder)
        video_path = os.path.join('.', self.out_folder)
        images_to_video(img_path, video_path)



""" ***********************************************************************************
MAIN
User specify configuration
Run pattern formation
*********************************************************************************** """
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-plate-size",
                        help="Tuple x_max, y_max", 
                        type=str)

    parser.add_argument("-n-iter-dla",
                        help="Scalar", 
                        type=int)

    parser.add_argument("-n-iter-eden",
                        help="Scalar",
                        type=int)

    parser.add_argument("-starter",
                        help="Tuple x0,y0", 
                        type=str)

    parser.add_argument("-dla-attractor",
                        help="none, circle, line",
                        type=str)

    parser.add_argument("-dla-r-spawn",
                        help="Scalar, radius of circle where particles are spawned",
                        type=int)

    parser.add_argument("-dla-r-kill",
                        help="Scalar, radius of circle where if outside particles are respawned",
                        type=int)

    parser.add_argument("-dla-r-jump",
                        help="Scalar, radius of circle where if outside particles are moving fast",
                        type=int)

    parser.add_argument("-checkpoint",
                        help="Number of plates to be saved during pattern forming",
                        type=int)

    parser.add_argument("-out-folder",
                        help="Folder where plots throught iterations will be stored",
                        type=str)

    args = parser.parse_args()

    # plate size
    plate_size = args.plate_size
    plate_size = plate_size.split(',')
    plate_size = [int(x) for x in plate_size]

    # n_iter: DLA, EDEN
    n_iter_eden = args.n_iter_eden
    n_iter_dla = args.n_iter_dla

    # starter
    starter = args.starter
    starter = starter.split(',')
    starter = np.array([int(x) for x in starter])

    # dla attractor
    dla_attractor = args.dla_attractor

    # dla spawn, kill, jump
    dla_r_spawn = args.dla_r_spawn
    dla_r_kill = args.dla_r_kill
    dla_r_jump = args.dla_r_jump

    # checkpoint, out folder
    checkpoint = args.checkpoint
    out_folder = args.out_folder

    # test print
    print("INPUT:")
    print("Plate size:", plate_size)
    print("n_iter_eden, n_iter_dla:", n_iter_eden, n_iter_dla)
    print("Starter:", starter)
    print("DLA: attractor, spawn_r, kill_r, jump_r:", dla_attractor, dla_r_spawn, dla_r_kill, dla_r_jump)
    print("Out folder, checkpoint", out_folder, checkpoint)


    # configure pattern formation
    dla_eden = DLA_EDEN(plate_size, 
                        n_iter_eden, 
                        n_iter_dla, 
                        starter, 
                        dla_attractor, 
                        dla_r_spawn,
                        dla_r_kill, 
                        dla_r_jump,
                        checkpoint,
                        out_folder)

    # grow pattern
    dla_eden.create_pattern()


""" *************************************************************************************
ROOT
************************************************************************************* """
if __name__ == '__main__':
    main()