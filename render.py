'''
John Sutor
September 25, 2020 

Script for generating many synthetic images 
'''
import os
from PIL import Image 
from skimage.io import imsave, imread
from albumentations.augmentations.transforms import GaussianBlur, GaussNoise, ColorJitter, Rotate  
# from albumentations.augmentations.geometric.rotate import Rotate
import albumentations
import numpy as np
import random 
from joblib import Parallel, delayed

BLENDER_DIR = "C:\Program Files\Blender Foundation\Blender 2.83"
NUM_RENDERS =  10

# Determine the working directory 
WORK_DIR = os.getcwd()

# Define the rendering function
render = lambda rc: os.system("blender -b --python " + WORK_DIR + "/synthblend.py -- -w " + WORK_DIR + " -rc " + str(rc + 1) + " -ra 3")

# Change to blender and run the render script 
os.chdir(BLENDER_DIR)
Parallel(n_jobs=-1, temp_folder='/tmp')(delayed(render)(i) for i in range(NUM_RENDERS))

def apply_background(img):
    if not '.txt' in img:  
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
            ColorJitter(),
            Rotate(limit=45, border_mode=2),
            GaussNoise()
        ])

        # Apply the transforms to the image 
        image = imread(WORK_DIR + '/renders/' + img)
        image = transforms(image=image)

        print(f"Applying background and augmentations to {WORK_DIR + '/renders/' + img}")

        imsave(WORK_DIR + '/renders/' + img, image["image"])

Parallel(n_jobs=-1, temp_folder='/tmp')(
    delayed(apply_background)(img) for img in os.listdir(WORK_DIR + "/renders/")
)
