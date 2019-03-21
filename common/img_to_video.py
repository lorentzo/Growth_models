""" *************************************************************************
IMPORTS
************************************************************************* """
import cv2 as cv
import os

""" **************************************************************************
PUBLIC
Takes folder with images and outputs file of video
************************************************************************** """
def images_to_video(img_path, video_path):
    
    # take all image names from folder
    images = os.listdir(img_path)
    
    # if no images quit
    if len(images) == 0:
        return
    
    # find shape of image
    src = os.path.join(img_path, images[0])
    img = cv.imread(src)
    img_shape = img.shape
    
    # create video writer
    PATH = os.path.join(video_path, "result.avi")
    out = cv.VideoWriter(PATH, cv.VideoWriter_fourcc('M','J','P','G'), 10, (img_shape[1], img_shape[0]))
    
    # sort images by numbers
    numbers = []
    for image in images:
        numbers.append(int(image.split(".")[0]))
        
    image_num = zip(images, numbers)
    image_num_s = sorted(image_num, key = lambda t: t[1])
    images, numbers = zip(*image_num_s)
    
    # take sorted images and save to video
    for image in images:
        print("SAVING...", image)
        src = os.path.join(img_path, image)
        img = cv.imread(src)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        out.write(img)
        
    out.release()