import SyntheticScene from synthetic_scene
SyntheticScene()

if __name__ == "__main__":
    # Load in the file
   

    # Scale up the object

    # Apply the mesh
    mat = bpy.data.materials.new(name=OBJ_TEX)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new("ShaderNodeTexImage")
    texImage.image = bpy.data.images.load(DIRECTORY + MODELS_DIR + OBJ_TEX)
    mat.node_tree.links.new(bsdf.inputs["Base Color"], texImage.outputs["Color"])

    # Assign it to object
    if bpy.context.scene.objects[OBJ_NAME].data.materials:
        bpy.context.scene.objects[OBJ_NAME].data.materials[0] = mat
    else:
        bpy.context.scene.objects[OBJ_NAME].data.materials.append(mat)

    # Add a camera
    camera = bpy.data.cameras.new("Camera")
    camera.show_background_images = True
    camera_obj = bpy.data.objects.new("Camera", camera)
    camera_obj.location = (3, -3, 4)
    camera_obj.rotation_euler = (0.785398, 0, 0.785398)
    bpy.context.scene.camera = camera_obj

    # Add the sun
    light = bpy.data.lights.new(name="Light", type="SUN")
    light_obj = bpy.data.objects.new("Light", light)
    light_obj.location = (3, -3, float("inf"))
    bpy.context.collection.objects.link(light_obj)
    bpy.context.view_layer.objects.active = light_obj

    # Import the background image
    bpy.ops.import_image.to_plane(files=[{"name": DIRECTORY + MODELS_DIR + BG_IMG}])
    background_obj = bpy.data.objects[BG_IMG.split(".jpg")[0]]
    background_obj.location = (-2, 2, -2)
    background_obj.rotation_euler = (0.785398, 0, 0.785398)
    background_obj.scale = (5, 5, 5)

    # Render the final image
    bpy.context.scene.render.filepath = DIRECTORY + "/renders/" + RENDER_IMG
    bpy.ops.render.render(write_still=True)