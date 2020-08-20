#!usr/bin/env python
# John Sutor
# July 21, 2020
"""
SynthBlend is used to establish and render scenes to be used for synthetic data purposes. 
It is meant to be extendable and customizable as to quickly get up-and-running generating 
synthetic data within Blender. This class makes assumptions about the way in which you 
structure your working directory, including all textures, models, and background images
within it. Background images must be included in their own directory. Models and textures 
should be included together in their own directory. Furthermore, textures should share the 
name of the object that they are to be applied to. This is intended for Blender >=2.80  
"""

# import bpy
import os
import random
import math
import mathutils
import sys
import argparse
import bpy 
from addon_utils import enable

def point_at(obj, target, roll=0):
  """
  Rotate obj to look at target

  :arg obj: the object to be rotated. Usually the camera
  :arg target: the location (3-tuple or Vector) to be looked at
  :arg roll: The angle of rotation about the axis from obj to target in radians. 

  Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)      
  """

  loc = obj.location
  # direction points from the object to the target
  direction = target.location - loc

  quat = direction.to_track_quat('-Z', 'Y')

  # /usr/share/blender/scripts/addons/add_advanced_objects_menu/arrange_on_curve.py
  quat = quat.to_matrix().to_4x4()
  rollMatrix = mathutils.Matrix.Rotation(roll, 4, 'Z')

  # remember the current location, since assigning to obj.matrix_world changes it
  loc = loc.to_tuple()
  obj.matrix_world = quat @ rollMatrix
  obj.location = loc

# Create the CLI via argparser
argv = sys.argv[sys.argv.index('--') + 1:]
parser = argparse.ArgumentParser(prog='synthblend', description='Render synthetic images via Blender')
parser.add_argument('-m', '--models', dest='models_directory', type=str)
parser.add_argument('-b', '--backgrounds', dest='backgrounds_directory', type=str)
parser.add_argument('-r', '--renders', dest='renders_directory', type=str)
parser.add_argument('-rc', '--render_count', dest='render_count', type=int)
parser.add_argument('-w', '--work', dest='work_directory', type=str, required=True)
args = parser.parse_known_args(argv)[0]

# Define the global variables 
work_directory = args.work_directory
blender_directory = os.getcwd()
backgrounds_directory = args.backgrounds_directory if args.backgrounds_directory else '/backgrounds/'
models_directory = args.models_directory if args.models_directory else '/models/'
renders_directory = args.renders_directory if args.renders_directory else '/renders/'
render_count = args.render_count if args.render_count else 0

# Clear the current scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Ensure that the import images as planes add-on is enabled
enable("io_import_images_as_planes")

# Load in the list of models, and randomly choose a model 
models_list = [file for file in os.listdir(work_directory + models_directory) if file[-4:] == '.dae']
model = random.choice(models_list)

# Load in the list of meshes, and randomly choose a mesh 
meshes_list = os.listdir(work_directory + models_directory + model[:-4])
mesh = random.choice(meshes_list)

# Load in the list of backgrounds 
backgrounds_list = os.listdir(work_directory + backgrounds_directory)

# Randomly choose a background for the model
background = random.choice(backgrounds_list)

# Load in the model
bpy.ops.wm.collada_import(filepath=work_directory + models_directory + model)

# Scale up the object 
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') 
bpy.data.objects[model[:-4]].scale = (1, 1, 1)

# Apply the mesh 
mat = bpy.data.materials.new(name=mesh[:-4])
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load(filepath=work_directory + models_directory + model[:-4] + "/" + mesh)
mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

# Assign it to object
if bpy.context.scene.objects[model[:-4]].data.materials:
  bpy.context.scene.objects[model[:-4]].data.materials[0] = mat
else:
  bpy.context.scene.objects[model[:-4]].data.materials.append(mat)
  
# Choose a random spherical coordinate to assign the camera and
# the background image to
phi = random.random() * math.pi / 2.
theta = random.random() * 2 * math.pi
radius = 3

# Convert the spherical coordinates to Cartesian coordinates
x = radius * math.sin(phi) * math.cos(theta)
y = radius * math.sin(phi) * math.sin(theta)
z = radius * math.cos(phi)
print("Camera at {},{},{} with rotation {} theta and {} phi".format(x, y, z, theta, phi))

# Add a camera
camera = bpy.data.cameras.new("Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
camera_obj.location = (x, y, z)
point_at(camera_obj, bpy.data.objects[model[:-4]])
bpy.context.scene.camera = camera_obj

# Add the sun
light = bpy.data.lights.new(name="Light", type='SUN')
light_obj = bpy.data.objects.new("Light", light)
light_obj.location = (3, -3, float('inf'))
bpy.context.collection.objects.link(light_obj)
bpy.context.view_layer.objects.active = light_obj

# Import the background image 
bpy.ops.import_image.to_plane(files=[{"name": work_directory + backgrounds_directory + background}])
background_obj = bpy.data.objects[background[:-4]]
background_obj.location = (-x, -y, -z)
point_at(background_obj, bpy.data.objects[model[:-4]])
background_obj.scale =  (4, 4, 4)

# Render the final image
bpy.context.scene.render.filepath = work_directory + renders_directory + 'render' + str(render_count) + '.jpg'
bpy.ops.render.render(write_still = True)