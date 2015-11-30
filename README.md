# Blender Lightbox 

Tools to create 2D animation within Blender 3D :)

This project's goal is to provide tools for use in traditional 2D animation.

##"Lightbox Animation Layer"


This add-on creates transparent "layers" ready to draw. Intended use is to create cleanups or final images from pencil or grease-pencil 
tests.
Once you have finished your tests, you can either scan your pages, or render your grease-pencil animation, load them as Background Image in 3D View, and then run this add-on.

At startup you are prompted to choose a folder to store all your frames for each layer. You need to set width and height 
resolution as well as start and end frame of sequence. The script will create a plane with proper material and textures where you can draw freely, as well as the required BLANK image sequence files (located in the provided path). 

If you have already set a Background Image as reference in viewport (including animation settings from a Sequence), you can choose to use it.

Once set, you can enter Texture Paint mode to start painting your frames. Surf the timeline to paint along the animation. From Image Editor you can save your work clicking on Image > Save Sequence menu item.

##TO DO -

* Assign different 3D layers for every created lightbox layer
* Onion skinning

##Known problems:

* For any NEW Image Editor window you need to set "start frame" of sequence and autorefresh option manually.
* If you create a sequence and then rename it, the original files will not be deleted.
* To see your drawing in Image Editor you need to enter/leave edit mode in the generated plane in order to force a refresh
* When you go off-limits the planes will turn pink, and sometimes you need to toggle Edit Mode for Blender to refresh viewports.


