# SynthBlend
A library for generating simple synthetic images from withing Blender. Imposes a 3D model onto a predetermined background

## Getting Started
There are no external dependencies to install for ```synthblend.py```, though if they exist in the future, they may be installed with 
```
pip install -r requirements.txt
```
To start running the script, you must change your current directory into where your blender script is located. For example, 
```console
$ cd "C:\Program Files\Blender Foundation\Blender 2.83"
```
Next, run the script by specifying running a Python script in Blender in headless mode. For a basic working script (assuming that your synthblend directory is stored at ```C:\synthblend\```), run 
```console
$ .\blender -b --python C:\synthblend\synthblend.py -- -w C:\synthblend\synthblend.py
```
This will generate an image taken from a random angle, and output it to ```C:\synthblend\renders\```

## Flags
You must run the synthblend method via the command line. In order to do so, you must first change directory into the location of your blender install. There, run the command ```.\blender -b --python <LOCATION OF SYNTHBLEND.PY> -- <ADDITIONAL ARGUMENTS>```. In the additional arguments, you must at least specify the working directory, i.e., where the ```synthblend.py``` script and the backgrounds, models, and renders directories are located. The flags for this command line tool are 
```console
-w | --work 
```
Specifies the working directory (where to find the other subdirectories)
```console
-b | --backgrounds 
```
Specifies the directory under the working directory where the background images can be found
```console
-m | --models 
```
Specifies the directory under the working directory where the .dae models and their associated meshes can be found
```console
-r | --renders 
```
Specifies the directory under the working directory where the final renders will be outputted
```console
-ra | --radius 
```
Specifies the spherical coordinate radius about which the camera-background system rotates
```console
-rc | --render_count 
```
Specifies the current count of the renders generated. **NOTE** This will not create more renders, this is only useful as a naming convention when generating large amounts of synthetic data. 
```console
-pmin | --phi_min 
```
Specifies the minimum angle phi (angle from the vertical), in radians, to rotate the camera-background system. Must be between 0 and pi / 2, inclusive.
```console
-pmax | --phi_max 
```
Specifies the maximum angle phi (angle from the vertical), in radians, to rotate the camera-background system. Must be between 0 and pi / 2, inclusive.
```console
-tmin | --theta_min 
```
Specifies the minimun angle theta (angle about the horizontal), in radians, to rotate the camera-background system. Must be between 0 and 2 * pi, inclusive.
```console
-tmax | --theta_max 
```
Specifies the maximum angle theta (angle about the horizontal), in radians, to rotate the camera-background system. Must be between 0 and 2 * pi, inclusive.

## Model Directory Structure
Although there is some degree of lee-way in how you choose to organize your directories, the models directory is strict in terms of how files and subdirectories within it should be formatted. Within the models directory, models should be made available in the ```.dae``` file format. Additionally, each ```.dae``` object should have the same name as its accompanying file. Otherwise, blender will not be able to locate the object. To specify the meshes applicable to each object, create a directory within the models directory that shares the same name as the ```.dae``` file. In this directory that contains the meshes to be applied at random to the ```.dae``` model, the naming conventions for the image formats does not matter.