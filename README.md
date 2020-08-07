# SynthBlend
A library for generating simple synthetic images from withing Blender. Imposes a 3D model onto a predetermined background

## Getting Started
You should have python >= 3.6 installed on your local machine. There are currently no package requirements for the library, though if they exist in the future, they may be installed with 
```
pip install -r requirements.txt
```

## SyntheticScene Class
The synthetic scene class currently supports two methods, a ```render()``` method and a ```clear()``` method. The ```render()``` method renders a single scene according to the specified arguments, and the ```clear()``` method clears the scene prior to the next render.