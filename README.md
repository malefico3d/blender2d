# blender2d
Tools to create 2D animation within Blender 3D :)

This project objective is to provide several tools for use in traditional 2D animation.

"2D Animation Layer"
--------------------

This add-on creates a transparent "layer" ready to draw. Intended use is to create cleanups or final images from pencil or grease-pencil tests.
Once you have finished your tests, you can either scan your pages, or render your grease-pencil animation, load them as Background Image in 3D View, and then run this add-on.

First you need to set width and height resolution as well as start and end frame of sequence. It will create a plane with proper material and textures where you can draw freely, as well as the required BLANK image sequence files (located in the provided path). 

Once set, you can enter Texture Paint mode to start painting your frames. Surf the timeline to paint along the animation. From Image Editor you can save your work clicking on Image > Save Sequence menu item.

TODO - Known problems:
----------------------
* If path doesn't exist, script will crash. It's neither created or checked by script right now. You need to edit it in source file. 
* At start you need to manually set "Autorefresh" option on in both 3D view and Image Editor windows. This should be automatic in future versions.
* Sometimes (if there is no Image Editor window opened) you need to set "start frame" of sequence manually at "1".
* If you create a sequence and then rename it, the original files will not be deleted nor replaced.


