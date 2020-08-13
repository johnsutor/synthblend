# SynthBlend
A library for generating simple synthetic images from withing Blender. Imposes a 3D model onto a predetermined background

## Getting Started
You should have python >= 3.6 installed on your local machine. There are currently no package requirements for the library, though if they exist in the future, they may be installed with 
```
pip install -r requirements.txt
```

## SyntheticScene Class
You must run the synthblend method via the command line. In order to do so, you must first change directory into the location of your blender install. There, run the command ```.\blender -b --python <LOCATION OF SYNTHBLEND.PY> -- <ADDITIONAL ARGUMENTS>```. In the additional arguments, you must at least specify the working directory, i.e., where the ```synthblend.py``` script and the backgrounds, models, and renders directories are located. You may also specify unique names for the backgrounds, models, and renders directories via the flags ```-b```, ```-m```, and ```-r```, respectively. 