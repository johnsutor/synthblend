# SynthBlend
A library for generating simple synthetic images from withing Blender. Imposes a 3D model onto a predetermined background

## Getting Started
There are no external dependencies to install for ```synthblend.py```, though if they exist in the future, they may be installed with 
```
pip install -r requirements.txt
```

## SyntheticScene Class
You must run the synthblend method via the command line. In order to do so, you must first change directory into the location of your blender install. There, run the command ```.\blender -b --python <LOCATION OF SYNTHBLEND.PY> -- <ADDITIONAL ARGUMENTS>```. In the additional arguments, you must at least specify the working directory, i.e., where the ```synthblend.py``` script and the backgrounds, models, and renders directories are located. You may also specify unique names for the backgrounds, models, and renders directories via the flags ```-b```, ```-m```, and ```-r```, respectively. 

## Model Directory Structure
Although there is some degree of lee-way in how you choose to organize your directories, the models directory is strict in terms of how files and subdirectories within it should be formatted. Within the models directory, models should be made available in the ```.dae``` file format. Additionally, each ```.dae``` object should have the same name as its accompanying file. Otherwise, blender will not be able to locate the object. To specify the meshes applicable to each object, create a directory within the models directory that shares the same name as the ```.dae``` file. In this directory that contains the meshes to be applied at random to the ```.dae``` model, the naming conventions for the image formats does not matter.