"""
John Sutor
September 25, 2020 

Script for generating many synthetic images 
"""
import os
import argparse
from PIL import Image
from imageio import imread, imsave
from albumentations.augmentations.transforms import (
    GaussNoise,
    HueSaturationValue,
    RandomBrightnessContrast,
)
import albumentations
import numpy as np
import random
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument(
    "--bounding_box",
    required=False,
    type=str,
    help="Bounding box format to use. \nOptions: ('COCO' | 'YOLO') \nDefault none",
)
parser.add_argument(
    "--img_size",
    required=False,
    type=int,
    help="Size, in pixels, of the square image to create \nDefault 1024",
)
parser.add_argument(
    "--models", 
    required=False,
    type=str,
    help="Directory of the models to render \nDefault './models'",
)
parser.add_argument("--phi_min", dest="phi_min", type=float)
parser.add_argument("--phi_max", dest="phi_max", type=float)



options = parser.parse_args()

BLENDER_DIR = "C:\Program Files\Blender Foundation\Blender 2.92"
NUM_RENDERS = 1000

# Determine the working directory
WORK_DIR = os.getcwd()

# Define the rendering function
render = lambda rc: os.system(
    "blender -b --python "
    + WORK_DIR
    + "/synthblend.py -- -w "
    + WORK_DIR
    + " -rc "
    + str(rc + 1)
    + " -ra 3 ims 256"
)

# Change to blender and run the render script
os.chdir(BLENDER_DIR)
Parallel(n_jobs=-1, temp_folder="/tmp")(delayed(render)(i) for i in range(NUM_RENDERS))


def apply_background(img):
    if ".png" in img:
        # Import the render
        render = Image.open(WORK_DIR + "/renders/" + img).convert("RGBA")
        rw, rh = render.size

        # Choose a random background
        background = random.choice(os.listdir(WORK_DIR + "/backgrounds/"))
        background = Image.open(WORK_DIR + "/backgrounds/" + background).convert("RGBA")
        bw, bh = render.size

        # Resize the background to match the render
        background = background.resize((rw, rh))

        # Center crop the background based on the render size
        # background = background.crop(((bw - rw) / 2, (bh - rh)/2, (bw + rw)/2, (bh + rh)/2))

        # Merge the background and the render
        background.paste(render, (0, 0), mask=render)
        background.save(WORK_DIR + "/renders/" + img)

        # Set the image transforms
        transforms = albumentations.Compose(
            [
                GaussNoise(),
                # HorizontalFlip(),
                # Rotate(limit=45),
                HueSaturationValue(hue_shift_limit=5, sat_shift_limit=10, val_shift_limit=50),
                RandomBrightnessContrast(),
            ]
        )

        # Apply the transforms to the image
        image = imread(WORK_DIR + "/renders/" + img, pilmode="RGB")
        image = transforms(image=image)

        print(
            f"Applying background and augmentations to {WORK_DIR + '/renders/' + img}"
        )

        imsave(WORK_DIR + "/renders/" + img, image["image"])


Parallel(n_jobs=-1, temp_folder="/tmp")(
    delayed(apply_background)(img) for img in os.listdir(WORK_DIR + "/renders/")
)
