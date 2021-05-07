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
import json
import bpy
import bpy_extras
from addon_utils import enable
from datetime import datetime

# Create the CLI via argparser
argv = sys.argv[sys.argv.index("--") + 1 :]
parser = argparse.ArgumentParser(
    prog="synthblend", description="Render synthetic images via Blender"
)
parser.add_argument("-m", "--models", dest="models_directory", type=str)
parser.add_argument("-bb", "--bounding_box", dest="bounding_box", type=str)
parser.add_argument("-r", "--renders", dest="renders_directory", type=str)
parser.add_argument("-ra", "--radius", dest="radius", type=float)
parser.add_argument("-rc", "--render_count", dest="render_count", type=int)
parser.add_argument("-pmin", "--phi_min", dest="phi_min", type=float)
parser.add_argument("-pmax", "--phi_max", dest="phi_max", type=float)
parser.add_argument("-tmin", "--theta_min", dest="theta_min", type=float)
parser.add_argument("-tmax", "--theta_max", dest="theta_max", type=float)
parser.add_argument("-ims", "--img_size", dest="img_size", type=int)
parser.add_argument("-sp", "--scale_param", dest="scale_param", type=float)
parser.add_argument("-w", "--work", dest="work_directory", type=str, required=True)
parser.add_argument("-s", "--shadow", dest="shadow", type=bool)

args = parser.parse_known_args(argv)[0]

# Define the global variables
work_directory = args.work_directory
blender_directory = os.getcwd()
bounding_box = args.bounding_box if args.bounding_box else "YOLO"
models_directory = args.models_directory if args.models_directory else "/models/"
renders_directory = args.renders_directory if args.renders_directory else "/renders/"
render_count = args.render_count if args.render_count else 0
radius = args.radius if args.radius else 4
shadow = args.shadow if args.shadow else False
img_size = args.img_size if args.img_size else 1024
scale_param = args.scale_param if args.scale_param else 0.3

# Define the angle constraints
phi_min = args.phi_min if args.phi_min else 0.0
phi_max = args.phi_max if args.phi_max else math.pi / 2.0
theta_min = args.theta_min if args.theta_min else 0.0
theta_max = args.theta_max if args.theta_max else 2.0 * math.pi

# Clear the current scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Ensure that the import images as planes add-on is enabled
# enable("io_import_images_as_planes")

# Load in the list of models, and choose one based on the render count
print(render_count - 1)
models_list = [folder for folder in os.listdir(work_directory + models_directory)]
model_folder = models_list[(render_count - 1) % len(models_list)]
model = [
    f
    for f in os.listdir(work_directory + models_directory + model_folder)
    if f[-4:] == ".dae"
][0]

# Load in the model
bpy.ops.wm.collada_import(
    filepath=work_directory + models_directory + model_folder + "/" + model
)

# Set the default scale for the object
bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
bpy.data.objects[model[:-4]].scale = (1, 1, 1)

# Randomly modify the scale (on all axes)
scale = scale_param * (2 * random.random() - 1)
bpy.data.objects[model[:-4]].scale = (1 + scale_param, 1 + scale_param, 1 + scale_param)

# Set objects color to black by default
for obj in bpy.data.objects.keys():
    for slot in bpy.data.objects[obj].material_slots:
        new_mat = bpy.data.materials.new(name="black")
        new_mat.diffuse_color = (0, 0, 0, 1)
        slot.material = new_mat
    print(bpy.data.objects[obj].data)
    bpy.data.objects[obj].color = (1, 0, 0, 1)

try:
    # Apply the default object mesh
    mesh = [
        f
        for f in os.listdir(work_directory + models_directory + model_folder)
        if f[-4:] in [".png", ".jpg", "jpeg"]
    ][0]

    # Apply the mesh
    mat = bpy.data.materials.new(name=mesh[:-4])
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new("ShaderNodeTexImage")
    texImage.image = bpy.data.images.load(
        filepath=work_directory + models_directory + model[:-4] + "/" + mesh
    )
    mat.node_tree.links.new(bsdf.inputs["Base Color"], texImage.outputs["Color"])

    # Assign it to object
    if bpy.context.scene.objects[model[:-4]].data.materials:
        bpy.context.scene.objects[model[:-4]].data.materials[0] = mat
    else:
        bpy.context.scene.objects[model[:-4]].data.materials.append(mat)

except:
    print("No mesh found...")

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
y += 0.1 * random.random() * y
z += 0.1 * random.random() * z

# Add a camera
camera = bpy.data.cameras.new("Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
camera_obj.location = (x, y, z)
camera_obj.rotation_euler = (phi, 0.0, theta + math.pi / 2)
bpy.context.scene.camera = camera_obj

# Add the sun
light = bpy.data.lights.new(name="Light", type="SUN")
light.energy = 2
light_obj = bpy.data.objects.new("Light", light)
light_obj.location = (x, y, float("inf"))
# light_obj.scale = (radius, radius, 1)
# light_obj.rotation_euler = (phi, 0., theta + math.pi / 2)
bpy.context.collection.objects.link(light_obj)
bpy.context.view_layer.objects.active = light_obj

# Set the background of the scene as transparent
bpy.context.scene.render.film_transparent = True

if shadow:
    # Add the image shadow
    bpy.ops.mesh.primitive_plane_add(
        enter_editmode=False,
        align="WORLD",
        location=(0, 0, min_z + bpy.context.scene.objects[model[:-4]].location[-1]),
    )
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
    bsdf_diffuse_2.inputs[0].default_value = (0, 0, 0, 1)

    # Link the mixer to the BSDF Transparent and the BW Converter
    node_tree.links.new(color_ramp.outputs[0], mixer.inputs[0])
    node_tree.links.new(bsdf_diffuse_2.outputs[0], mixer.inputs[1])
    node_tree.links.new(bsdf_transparent.outputs[0], mixer.inputs[2])

    # Create an output and link it
    output = node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    node_tree.links.new(mixer.outputs[0], output.inputs[0])

    # Set the blend method for the material
    plane_material.blend_method = "BLEND"

# Set the render size
bpy.context.scene.render.resolution_x = img_size
bpy.context.scene.render.resolution_y = img_size

# Render the final image
bpy.context.scene.render.filepath = (
    work_directory + renders_directory + "render_" + str(render_count).zfill(5) + ".jpg"
)
bpy.context.scene.render.image_settings.color_depth = '16'
bpy.ops.render.render(write_still=True)

# Determine the bounding box
if bounding_box is not None:
    xlist, ylist = [], []
    # Print all vertices
    for v in bpy.data.objects[model[:-4]].data.vertices:
        coord = bpy.data.objects[model[:-4]].matrix_world @ v.co

        # Get the location on the final rendered image
        img_loc = bpy_extras.object_utils.world_to_camera_view(
            bpy.context.scene, bpy.context.scene.camera, coord
        )
        xlist.append(img_loc.x)
        ylist.append(img_loc.y)

    # Choose the bounding coordinates
    min_x = 0.0 if min(xlist) < 0.0 else 1.0 if min(xlist) > 1.0 else min(xlist)
    max_x = 0.0 if max(xlist) < 0.0 else 1.0 if max(xlist) > 1.0 else max(xlist)
    min_y = 0.0 if min(ylist) < 0.0 else 1.0 if min(ylist) > 1.0 else min(ylist)
    max_y = 0.0 if max(ylist) < 0.0 else 1.0 if max(ylist) > 1.0 else max(ylist)

    # Output coordinates YOLO format
    if bounding_box == "YOLO":
        with open(
            work_directory
            + renders_directory
            + "render_"
            + str(render_count).zfill(5)
            + ".txt",
            "w",
        ) as f:
            f.write(
                f"0 {str((max_x - min_x)/2 + min_x)} {str(1 - ((max_y - min_y)/2 + min_y))} {str(max_x - min_x)} {str(max_y - min_y)}"
            )

    # Output coordinates to COCO segmentation format
    elif bounding_box == "COCO":
        now = datetime.now()
        date = (
            now.strftime("%d")
            + "/"
            + now.strftime("%m")
            + "/"
            + now.strftime("%Y")
        )

        # Create the basic image data
        img_data = (
            {
                "license": 1,
                "file_name": "render_" + str(render_count).zfill(5) + ".jpg",
                "coco_url": "https://github.com/johnsutor/synthblend",
                "height": img_size,
                "width": img_size,
                "date_captured": date,
                "flickr_url": "https://github.com/johnsutor/synthblend",
                "id": str(render_count).zfill(5),
            },
        )

        # Shift vertices to match image size
        xlist = [img_size * x for x in xlist]
        ylist = [img_size * y for y in ylist]

        # Calculate the convex hull (https://code.activestate.com/recipes/117225-convex-hull-and-diameter-of-2d-point-sets/)
        def orient(p, q, r):
            # + is clockwise, 0 if colinear, - if counterclockwise
            return (q[1]-p[1])*(r[0]-p[0]) - (q[0]-p[0])*(r[1]-p[1])

        '''Graham scan to find upper and lower convex hulls of a set of 2d points.'''
        U = []
        L = []
        points = zip(xlist, ylist).sort()
        for p in points:
            while len(U) > 1 and orient(U[-2],U[-1],p) <= 0: U.pop()
            while len(L) > 1 and orient(L[-2],L[-1],p) >= 0: L.pop()
            U.append(p)
            L.append(p)

        hull = U.extend(L)

        # Calculate the image area based on the shoelace formula
        area = abs(
            0.5
            * (
                sum([x * y for x, y in zip(xlist[:-1], ylist[1:])])
                + xlist[-1] * ylist[0]
                - sum([x * y for x, y in zip(xlist[1:], ylist[:-1])])
                - xlist[0] * ylist[-1]
            )
        )

        # Create image annotation data
        img_annotation = {
            "segmentation": [
                coord
                for coords in [(x, y) for x, y in zip(xlist, ylist)]
                for coord in coords
            ],
            "area": area,
            "iscrowd": 0,
            "image_id": str(render_count).zfill(5),
            "bbox": [max_x, max_y, max_x - min_x, max_y - min_y],
            "category_id": models_list.index(model_folder),
            "id": str(render_count).zfill(5),
        }

        # Check if annotation file already exists
        if os.path.exists(work_directory + renders_directory + "coco.json"):
            # Load in the file
            annotations = json.load(
                open(work_directory + renders_directory + "coco.json", "r")
            )

        # File doesn't exist, create
        else:
            categories = [
                {"supercategory": models_list[i], "id": i, "name": models_list[i]}
                for i in range(len(models_list))
            ]
            annotations = {
                "info": {
                    "description": "Synthblend Dataset",
                    "url": "https://github.com/johnsutor/synthblend",
                    "version": "1.0",
                    "year": now.strftime("%Y"),
                    "contributor": "Synthblend",
                    "date_created": date,
                },
                "licenses": [
                    {
                        "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/",
                        "id": 1,
                        "name": "Attribution-NonCommercial-ShareAlike License",
                    },
                ],
                "images": [],
                "annotations": [],
                "categories": categories,
                "segment_info": [],
            }

        annotations["images"].append(img_data)
        annotations["annotations"].append(img_annotation)

        with open(work_directory + renders_directory + "coco.json", "w") as fp:
            json.dump(annotations, fp)
