bl_info = {
    "name": "create_anim_layer",
    "author": "Claudio Andaur(malefico)",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "Add > Mesh > 2D Animation Layer",
    "description": "Creates a plane and an image sequence to use in 2D animation.",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}

# -----------------------------------------------------------------------------
# This script is based on "Import Images as Planes" script by Florian Meyer et al.
# -----------------------------------------------------------------------------

import bpy
from bpy.types import Operator
import mathutils
import os.path
import collections

from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       CollectionProperty,
                       )

from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy_extras.image_utils import load_image



class IMPORT_OT_anim_layer(Operator, AddObjectHelper):
    """Creates a plane and an image sequence to use is 2D animation"""
    bl_idname = "animation.create_anim_layer"
    bl_label = "Creates a 2D Animation Layer"
    bl_options = {'REGISTER', 'UNDO'}

   #----------------------------------------------------------------------------
   # IMPORTANT: EDIT THIS DEFAULT FILE PATH TO AVOID CRASH ON STARTUP
   #
   # The path must EXIST, it's not created nor checked by the script right now.
   # This is where all image sequence files will be created.
   # ---------------------------------------------------------------------------

    filepath = StringProperty(name="Image Folder", default="/home/alumno/script", maxlen = 1024)
    # ********************************************************************   

    start_frame = IntProperty(name="Start", min=1, soft_min=1, default=1, description="Start frame of animation layer")
    end_frame = IntProperty(name="End", min=1, soft_min=1, default=2, description="End frame of animation layer")

  

    layer_name = StringProperty(name="Layer Name", default= "INK", maxlen=1024)
    same_res = BoolProperty( name="Set layer resolution", description = "By default uses same resolution as Background Image", default= False)
    same_length = BoolProperty( name="Set animation length", description = "By default uses same animation length as Background Image", default= False)
    frame_width = FloatProperty(name="Width", description="Width of frame layer in pixels", default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')
    frame_height = FloatProperty(name="Height", description="Height of frame layer in pixels", default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')


    # --------
    # Options.

    align_offset = FloatProperty(name="Offset", min=0, soft_min=0, default=0.1, description="Space between Planes")
    

    def draw(self, context):
        engine = context.scene.render.engine
        layout = self.layout

        box = layout.box()
        box.label("2D Animation Layer Settings:", icon='TEXTURE')
        box.prop(self, "layer_name")

        box.prop(self, "filepath")

        row = box.row()
        row.prop(self, "same_length")
        sub = box.row()
        sub.active = self.same_length
        sub.prop(self, "start_frame")
        sub.prop(self, "end_frame")
        
        row = box.row()
        row.prop(self, "same_res")
        sub = box.row()
        sub.active = self.same_res
        sub.prop(self, "frame_width")
        sub.prop(self, "frame_height")



    #def invoke(self, context, event):
    #    self.update_extensions(context)
    #    context.window_manager.fileselect_add(self)
    #    return {'RUNNING_MODAL'}

    def execute(self, context):
        if not bpy.data.is_saved:
            self.relative = False

        # the add utils don't work in this case because many objects are added disable relevant things beforehand
        editmode = context.user_preferences.edit.use_enter_edit_mode
        context.user_preferences.edit.use_enter_edit_mode = False
        if context.active_object and context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        layer = self.create_image_plane(context)
        context.user_preferences.edit.use_enter_edit_mode = editmode
        return {'FINISHED'}

         

# Principal
    def create_image_plane(self, context):
        engine = context.scene.render.engine
        y = self.frame_height
        x = self.frame_width
        bpy.ops.mesh.primitive_plane_add('INVOKE_REGION_WIN')
        
        layer = context.scene.objects.active
        # Why does mesh.primitive_plane_add leave the object in edit mode???
        
        if layer.mode is not 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        layer.dimensions = x, y, 0.0
        layer.name = self.layer_name
        layer.location = [0.0, 0.0, 0.0] # Crea capa en el origen de coordenadas
        bpy.ops.object.transform_apply(scale=True)
        layer_material = self.create_image_sequence(context)

        # Assign it to object
        if len(layer.data.materials):
            # assign to 1st material slot
            layer.data.materials[0] = layer_material
        else:
            # no slots
            layer.data.materials.append(layer_material)

               
        return layer
 
    def create_image_sequence(self, context):
        #Esta funcion crea un datablock de imagen y una secuencia de archivos en blanco con la resolucion y nombre de la capa
        start = self.start_frame
        end = self.end_frame
        layername= self.layer_name
        filepath= self.filepath
        size = self.frame_width, self.frame_height
        # Creates image datablock with blank image data
        image = bpy.ops.image.new(name= layername, width=size[0], height=size[1], color=(0.0, 0.0, 0.0, 0.0), alpha=True, generated_type='BLANK', float=False, gen_context='NONE', use_stereo_3d=False)
        # Reads data from created datablock
        image_data = bpy.data.images[layername]
        ob_layer = context.scene.objects.active
        ob_layer.data.uv_textures.new()
        ob_layer.data.uv_textures[0].data[0].image = image_data
        # Creates PNG files for all frames in sequence
        for i in range (start, end):
            name = layername + "-" + str(i).zfill(5) + ".PNG"
            path = os.path.join(filepath,name)

            image_data.filepath_raw = path
            image_data.file_format = 'PNG'
            image_data.save()
            print("Saving image: ", path)
        # Set options for Image Datablock
        image_data.source = 'SEQUENCE'
        image_data.frame_start = start
        image_data.frame_end = end
        image_data.use_alpha = True
        image_data.alpha_mode = 'PREMUL'
        
        layer_material = bpy.data.materials.new(self.layer_name)
        layer_material.alpha = 0.0
        layer_material.use_shadeless = True
        layer_material.transparency_method = 'Z_TRANSPARENCY'
        layer_material.use_transparency = True

        image_texture = bpy.data.textures.new(self.layer_name, type= 'IMAGE')
        image_texture.image = image_data
        
#        bpy.data.textures[image_data.name].use_autorefresh = True
#        bpy.data.textures[image_data.name].frame_start = start
        
        mat_tex = layer_material.texture_slots.add()
        mat_tex.texture = image_texture
        mat_tex.texture_coords = 'UV'
        mat_tex.use_map_color_diffuse = True
        mat_tex.diffuse_color_factor = 1.0
        mat_tex.use_map_alpha = True
        mat_tex.alpha_factor = 1.0
        
               
        return layer_material

 
                    

# -----------------------------------------------------------------------------
# Register
def create_anim_layer_button(self, context):
    self.layout.operator(IMPORT_OT_anim_layer.bl_idname,
                         text="Creates a 2D Animation Layer", icon='TEXTURE')


def register():
    bpy.utils.register_module(__name__)
    #bpy.types.INFO_MT_file_import.append(create_anim_layer_button)
    bpy.types.INFO_MT_mesh_add.append(create_anim_layer_button)


def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.types.INFO_MT_file_import.remove(create_anim_layer_button)
    bpy.types.INFO_MT_mesh_add.remove(create_anim_layer_button)


if __name__ == "__main__":
    register()
