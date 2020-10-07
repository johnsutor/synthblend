'''
John Sutor
September 25, 2020 

Script for generating many synthetic images 
'''
import os 

BLENDER_DIR = "/home/mlpc/blender/blender-2.83.2-linux64"
NUM_RENDERS =  3 

# Determine the working directory 
WORK_DIR = os.getcwd()

# Change to blender and run the render script 
os.chdir(BLENDER_DIR)
for i in range(NUM_RENDERS):
    os.system("blender -b --python " + WORK_DIR + "/synthblend.py -- -w " + WORK_DIR + " -rc " + str(i + 1) + " -bb YOLO -ra 3 -pmin 1.0471975512")