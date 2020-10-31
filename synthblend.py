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
import bpy_extras
from addon_utils import enable

# Create the CLI via argparser
argv = sys.argv[sys.argv.index('--') + 1:]
parser = argparse.ArgumentParser(prog='synthblend', description='Render synthetic images via Blender')
parser.add_argument('-m', '--models', dest='models_directory', type=str)
parser.add_argument('-bb', '--bounding_box', dest='bounding_box', type=str)
parser.add_argument('-r', '--renders', dest='renders_directory', type=str)
parser.add_argument('-ra', '--radius', dest='radius', type=float)
parser.add_argument('-rc', '--render_count', dest='render_count', type=int)
parser.add_argument('-pmin', '--phi_min', dest='phi_min', type=float)
parser.add_argument('-pmax', '--phi_max', dest='phi_max', type=float)
parser.add_argument('-tmin', '--theta_min', dest='theta_min', type=float)
parser.add_argument('-tmax', '--theta_max', dest='theta_max', type=float)
parser.add_argument('-w', '--work', dest='work_directory', type=str, required=True)
args = parser.parse_known_args(argv)[0]

# Define the global variables 
work_directory = args.work_directory
blender_directory = os.getcwd()
bounding_box = args.bounding_box if args.bounding_box else None
models_directory = args.models_directory if args.models_directory else '/models/'
renders_directory = args.renders_directory if args.renders_directory else '/renders/'
render_count = args.render_count if args.render_count else 0
radius = args.radius if args.radius else 4

print('bounding box is ', bounding_box) 

# Define the angle constraints 
phi_min = args.phi_min if args.phi_min else 0.
phi_max = args.phi_max if args.phi_max else math.pi / 2.
theta_min = args.theta_min if args.theta_min else 0.
theta_max = args.theta_max if args.theta_max else 2. * math.pi

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

# Load in the model
bpy.ops.wm.collada_import(filepath=work_directory + models_directory + model)

# Scale up the object 
bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') 
bpy.data.objects[model[:-4]].scale = (1, 1, 1)

# Set objects color to black by default 
for obj in bpy.data.objects.keys():
  for slot in bpy.data.objects[obj].material_slots:
      new_mat = bpy.data.materials.new(name="black")
      new_mat.diffuse_color = (0,0,0, 1)
      slot.material = new_mat
  # print(dbpy.data.objects[obj].data)
  # bpy.data.objects[obj].color = (1, 0, 0, 1)

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

# Get the object's lower z bound to attach the plane to 
min_z = float("inf")
for p in bpy.context.scene.objects[model[:-4]].bound_box:
  if p[-1] < min_z:
    min_z = p[-1]

  
# Choose a random spherical coordinate to assign the camera and
# the background image to
phi = (phi_max - phi_min) * random.random() + phi_min
theta = (theta_max - theta_min) * random.random() + theta_min

# Convert the spherical coordinates to Cartesian coordinates
x = radius * math.sin(phi) * math.cos(theta)
y = radius * math.sin(phi) * math.sin(theta)
z = radius * math.cos(phi)

# Choose a random offset for the x, y, and z direction 
x += 0.1 * random.random() * x
y +=  0.1 * random.random() * y
z += 0.1 * random.random() * z

# Add a camera
camera = bpy.data.cameras.new("Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
camera_obj.location = (x, y, z)
camera_obj.rotation_euler = (phi, 0., theta + math.pi / 2)
bpy.context.scene.camera = camera_obj

# Add the sun
light = bpy.data.lights.new(name="Light", type='SUN')
# light.energy = 100
light_obj = bpy.data.objects.new("Light", light)
light_obj.location = (x, y, z)
# light_obj.scale = (radius, radius, 1)
# light_obj.rotation_euler = (phi, 0., theta + math.pi / 2)
bpy.context.collection.objects.link(light_obj)
bpy.context.view_layer.objects.active = light_obj

# Set the background of the scene as transparent 
bpy.context.scene.render.film_transparent = True

# Add the image shadow
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, min_z + bpy.context.scene.objects[model[:-4]].location[-1]))
plane = bpy.data.objects["Plane"]
# plane.scale = (1, 1, 1)

plane_material = bpy.data.materials.new(name="PlaneMaterial")
plane_material.use_nodes = True
plane.data.materials.append(plane_material)

# Clear all nodes to start 
if plane_material.node_tree:
    plane_material.node_tree.links.clear()
    plane_material.node_tree.nodes.clear()

# Edit the node tree
bpy.context.active_object.active_material = plane_material

node_tree = bpy.context.active_object.active_material.node_tree

bsdf_diffuse = node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
shader_to_rgb = node_tree.nodes.new(type="ShaderNodeShaderToRGB")

# Link the BSDF Diffuse to the RGB Converter
node_tree.links.new(bsdf_diffuse.outputs[0], shader_to_rgb.inputs[0])

color_ramp = node_tree.nodes.new(type="ShaderNodeValToRGB")

# Link the RGB Converter to the BW Converter
node_tree.links.new(shader_to_rgb.outputs[0], color_ramp.inputs[0])

mixer = node_tree.nodes.new(type="ShaderNodeMixShader")
bsdf_diffuse_2 = node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
bsdf_transparent = node_tree.nodes.new(type="ShaderNodeBsdfTransparent")

# Set the bsdf diffuse to black
bsdf_diffuse_2.inputs[0].default_value = (0,0,0,1)

# Link the mixer to the BSDF Transparent and the BW Converter
node_tree.links.new(color_ramp.outputs[0], mixer.inputs[0])
node_tree.links.new(bsdf_diffuse_2.outputs[0], mixer.inputs[1])
node_tree.links.new(bsdf_transparent.outputs[0], mixer.inputs[2])

# Create an output and link it 
output = node_tree.nodes.new(type="ShaderNodeOutputMaterial")
node_tree.links.new(mixer.outputs[0], output.inputs[0])

# Set the blend method for the material
plane_material.blend_method = 'BLEND'

# Render the final image
bpy.context.scene.render.filepath = work_directory + renders_directory + 'render_' + str(render_count).zfill(5) + '.jpg'
bpy.ops.render.render(write_still = True)

# Determine the bounding box
if bounding_box is not None: 
  xlist, ylist = [], []
  # Print all vertices 
  for v in bpy.data.objects[model[:-4]].data.vertices:
    coord = bpy.data.objects[model[:-4]].matrix_world @ v.co
    
    # Get the location on the final rendered image
    img_loc = bpy_extras.object_utils.world_to_camera_view(bpy.context.scene, bpy.context.scene.camera, coord)
    xlist.append(img_loc.x)
    ylist.append(img_loc.y)
      
  # Choose the bounding coordinates 
  min_x = 0. if min(xlist) < 0. else 1. if min(xlist) > 1. else min(xlist)
  max_x = 0. if max(xlist) < 0. else 1. if max(xlist) > 1. else max(xlist)
  min_y = 0. if min(ylist) < 0. else 1. if min(ylist) > 1. else min(ylist)
  max_y = 0. if max(ylist) < 0. else 1. if max(ylist) > 1. else max(ylist)

  # Output coordinates YOLO format
  if bounding_box == 'YOLO':
    with open( work_directory + renders_directory + 'render_' + str(render_count).zfill(5) + '.txt', 'w') as f:
      f.write(f'0 {str((max_x - min_x)/2 + min_x)} {str(1 - ((max_y - min_y)/2 + min_y))} {str(max_x - min_x)} {str(max_y - min_y)}')