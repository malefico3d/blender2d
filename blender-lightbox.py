bl_info = {
    "name": "Blender Lightbox",
    "author": "Claudio Andaur(malefico)",
    "version": (0, 0, 2),
    "blender": (2, 75, 0),
    "location": "View > Lightbox Layer",
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
import bpy.path 
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       )

from bpy_extras.object_utils import AddObjectHelper, object_data_add


def get_bg_images(): # Returns a list of available Background Images in 3D View
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space_data = area.spaces.active
            bgimages = space_data.background_images
            #
            #Uncomment for debuggin
            #------------------------
            #image = bgimages[0].image
            #print("Image path is: ", image.filepath)  
            return (bgimages)

class LB_Callback_Operator(Operator):
    bl_idname = "image.lb_callback_operator"
    bl_label = "LB create sequence callback"
    bl_options = {'REGISTER', 'UNDO'}
    
    name = StringProperty(default = '')
    frame_end = IntProperty()
    frame_start= IntProperty()
    frame_width = FloatProperty()
    frame_height = FloatProperty()
    filepath = StringProperty()

    def create_blank_sequence(self):
        # In order to draw freely along the timeline, we need to supply blank images for every
        # frame in the sequence so Blender doesn't show a Pink Texture
        # when the required image doesn't exist.
        layername = self.name
        start = self.frame_start
        end = self.frame_end
        userpath = os.path.dirname(self.filepath)
        print("user path es: ", userpath)
        w = int(self.frame_width)
        h = int(self.frame_height)
        image_data = bpy.data.images.new(name= layername, alpha=True, width=w, height=h)
        
        pixels = list(image_data.pixels)
        
        ## blank image
        pixels = [0.0] * (4 * w * h)

        # assign pixels
        image_data.pixels = pixels            
      
        for i in range (start, end):
            name = layername + "-" + str(i).zfill(5) + ".PNG"
            path = os.path.join(userpath,name)
            image_data.filepath_raw = path
            image_data.file_format = 'PNG'
            image_data.save()
            print("Saving image: ", path)
        return {'FINISHED'}    
       
    def execute(self, context):
        self.create_blank_sequence()
        return {'FINISHED'}    
            

# Principal
            
class VIEW3D_OT_lightbox_layer(Operator, AddObjectHelper):
    """Creates a plane and an image sequence to use is 2D animation"""
    bl_idname = "animation.lightbox_layer"
    bl_label = "Select a folder for saving images"
    bl_options = {'REGISTER', 'UNDO'}    
    
    layer_name = StringProperty(name="Layer Name", default= "INK", maxlen=1024)
    filepath = StringProperty(name="Image Folder", default="//", subtype = "DIR_PATH", maxlen = 1024)
    use_background = BoolProperty( name="Use Background Settings", description = "By default uses same resolution as Background Image", default= False)
    frame_width = FloatProperty(name="Width", description="Width of frame layer in pixels", default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')
    frame_height = FloatProperty(name="Height", description="Height of frame layer in pixels", default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')
    frame_start = IntProperty(name="Start", min=1, soft_min=1, default=1, description="Start frame of animation layer")
    frame_end = IntProperty(name="End", min=1, soft_min=1, default=2, description="End frame of animation layer")

    def create_lightbox_mat(self, context):
        # Creates a transparent material
        lightbox_mat = bpy.data.materials.new(self.layer_name)
        lightbox_mat.alpha = 0.0
        lightbox_mat.use_shadeless = True
        lightbox_mat.transparency_method = 'Z_TRANSPARENCY'
        lightbox_mat.use_transparency = True
        return lightbox_mat

    def create_image(self, context):
        layername = self.layer_name
        start = self.frame_start
        end = self.frame_end
        userpath = os.path.dirname(self.filepath)
        
        w = int(self.frame_width)
        h = int(self.frame_height)
        
        # Creates image datablock with blank image data
        #image = bpy.ops.image.new(name= layername, width=w, height=h, color=(0.0, 0.0, 0.0, 0.0), alpha=True)
        image_data = bpy.data.images.new(name= layername, alpha = True, width=w, height=h)
        #image_data = bpy.data.images[layername] # Lee datos de imagen
        #pixels = list(image_data.pixels)
        
        ## blank image
        #pixels = [0.0] * (4 * w * h)
        # flatten list
        #pixels = [chan for px in pixels for chan in px]

        # assign pixels
        #image_data.pixels = pixels            
        #print("Image to save is: ", image_data)
        
        ob_layer = context.scene.objects.active
        ob_layer.data.uv_textures.new() # Crea nueva textura UV
        ob_layer.data.uv_textures[0].data[0].image = image_data # asigna datos a canal de textura        
        
        # I need to save first frame of sequence so we 
        # can see something in 3D View, before creating whole sequence
        # WARNING: This will only be visible at frame_start.
        # Maybe I need to set current frame to frame_start as well

        name = layername + "-" + str(start).zfill(5) + ".PNG"
        path = os.path.join(userpath,name)
        image_data.filepath_raw = bpy.path.abspath(path)
        image_data.file_format = 'PNG'

        # Set options for Image Datablock
        image_data.source = 'SEQUENCE'
        image_data.frame_start = start
        image_data.frame_end = end
        image_data.use_alpha = True
        image_data.alpha_mode = 'PREMUL'       

        return image_data
        
        
    def create_lightbox_layer(self, context):

        y = 1.0
        x = self.frame_width / self.frame_height

        bpy.ops.mesh.primitive_plane_add('INVOKE_REGION_WIN')
        
        lightbox_layer = context.scene.objects.active
        # Why does mesh.primitive_plane_add leave the object in edit mode???
        
        if lightbox_layer.mode is not 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        lightbox_layer.dimensions = x, y, 0.0
        lightbox_layer.name = self.layer_name
        lightbox_layer.location = [0.0, 0.0, 0.0] # Creates layer at origin
        lightbox_layer.show_bounds = True
        lightbox_layer.draw_bounds_type = 'BOX' # Otherwise you wouldn't see where the image ends in 3D View if using Material draw mode.
        bpy.ops.object.transform_apply(scale=True)

        # Creates transparent material
        lightbox_material = self.create_lightbox_mat(context)  
        # Assign it to object
        if len(lightbox_layer.data.materials):
            # assign to 1st material slot
            lightbox_layer.data.materials[0] = lightbox_material
        else:
            # no slots
            lightbox_layer.data.materials.append(lightbox_material)
        
        # Creates image uvtexture and assigns it to material slot
        image = self.create_image(context) # image is image data from created datablock

        image_texture = bpy.data.textures.new(self.layer_name, type= 'IMAGE') # Creates image texture object
        image_texture.image = image
        image_texture.image_user.use_auto_refresh = True
        
		# If there is an Image Editor available, we set frame start and use_auto_refresh
		# In any NEW Image editor window we have to set this up manually

        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                space = area.spaces.active
                space.image_user.use_auto_refresh = True
                space.image_user.frame_start = self.frame_start
                
                break              
        mat_tex_slot = lightbox_material.texture_slots.add()
        mat_tex_slot.texture = image_texture
        
        mat_tex_slot.texture_coords = 'UV'
        mat_tex_slot.use_map_color_diffuse = True
        mat_tex_slot.diffuse_color_factor = 1.0
        mat_tex_slot.use_map_alpha = True
        mat_tex_slot.alpha_factor = 1.0      
        return lightbox_layer


            
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label("Lightbox Layer Settings:", icon='TEXTURE')
        box.prop(self, "layer_name", text = "Layer Name")
        box.prop(self, "filepath", text = "Image Folder")
        row = box.row()
        
        # If 3D View has a Background Image we might want to use same resolution
        # and sequence limits.
        row.prop(self, "use_background")
        if (self.use_background == True):
            bg_images = get_bg_images()
            if len(bg_images) == 0: # There is no background image to use
                self.use_background = False
                print("There is no Background Image set. Resolution and Animation values should be set by user.")
            else:
                # Use background image values
                #print("Background Sequence Image values will be used")
                image_data = bg_images[0].image # First background image data is used
                self.frame_width = image_data.size[0]
                self.frame_height = image_data.size[1]
                if image_data.source == 'SEQUENCE' or image_data.source == 'MOVIE':
                    self.frame_start = bg_images[0].image_user.frame_start
                    self.frame_end = bg_images[0].image_user.frame_start + bg_images[0].image_user.frame_duration

        row = box.row()
        row.prop(self, "frame_width")
        row.prop(self, "frame_height")
        row = box.row()
        row.prop(self, "frame_start")
        row.prop(self, "frame_end")
        
        row = box.row()
        op = row.operator("image.lb_callback_operator", text= "Create Image Sequence")
        op.name = self.layer_name
        op.frame_start = self.frame_start
        op.frame_end = self.frame_end
        op.frame_width = self.frame_width
        op.frame_height = self.frame_height
        op.filepath = self.filepath
        
    def execute(self, context):
        if not bpy.data.is_saved:
            self.relative = False
        # the add utils don't work in this case because many objects are added disable relevant things beforehand
        editmode = context.user_preferences.edit.use_enter_edit_mode
        context.user_preferences.edit.use_enter_edit_mode = False
        if context.active_object and context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
     
        layer = self.create_lightbox_layer(context) # Creates Ligthbox transparent plane with proper material and texture
        context.user_preferences.edit.use_enter_edit_mode = editmode        
        return {'FINISHED'}

# -----------------------------------------------------------------------------
# Register

def lightbox_layer_button(self, context):
    self.layout.operator(VIEW3D_OT_lightbox_layer.bl_idname, text="Create Lightbox Animation Layer", icon='TEXTURE')


def register():
    bpy.utils.register_class(LB_Callback_Operator)
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_view.append(lightbox_layer_button)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(CreateImageSequenceOperator)
    bpy.types.VIEW3D_MT_view.remove(lightbox_layer_button)

if __name__ == "__main__":
    register()
