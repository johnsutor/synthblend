'''
John Sutor
September 25, 2020 

Script for generating many synthetic images 
'''
import os
from PIL import Image 
from skimage.io import imsave, imread
from albumentations.augmentations.transforms import GaussianBlur
from albumentations.imgaug.transforms import IAAAdditiveGaussianNoise
import albumentations
import numpy as np
import random 

BLENDER_DIR = "C:\Program Files\Blender Foundation\Blender 2.83"
NUM_RENDERS =  10

# Determine the working directory 
WORK_DIR = os.getcwd()

# Change to blender and run the render script 
os.chdir(BLENDER_DIR)
for i in range(NUM_RENDERS):
    os.system("blender -b --python " + WORK_DIR + "/synthblend.py -- -w " + WORK_DIR + " -rc " + str(i + 1) + " -bb YOLO -ra 3 -pmin 1.0471975512")

# Add a background to each of the renders
for img in os.listdir(WORK_DIR + '/renders/'):
    if not '.txt' in img:  
        print('let\'s go')
        # Import the render
        render = Image.open(WORK_DIR + '/renders/' + img).convert("RGBA")
        rw, rh = render.size 

        # Choose a random background 
        background = random.choice(os.listdir(WORK_DIR + '/backgrounds/'))
        background = Image.open(WORK_DIR + '/backgrounds/' + background).convert("RGBA")
        bw, bh = render.size

        # Resize the background to match the render 
        background = background.resize((rw, rh))

        # Center crop the background based on the render size
        # background = background.crop(((bw - rw) / 2, (bh - rh)/2, (bw + rw)/2, (bh + rh)/2))
        
        # Merge the background and the render 
        background.paste(render, (0,0), mask=render)
        background.save(WORK_DIR + '/renders/' + img)

        # Set the image transforms
        transforms = albumentations.Compose([
            GaussianBlur(blur_limit=(3,5)),
            IAAAdditiveGaussianNoise()
        ])

        # Apply the Gaussian Filter to the image 
        image = imread(WORK_DIR + '/renders/' + img)
        
        image = transforms(image=image)

        imsave(WORK_DIR + '/renders/' + img, image["image"])