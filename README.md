A skeleton for making simple 3D games in Python and Pyglet.

Uses https://github.com/fogleman/Minecraft for camera controls but I've gone my own direction for things like collision detection. The collision detection is broadphase - using cylinders and boxes, a good starting point before doing more complicated and detailed tests.

It also has a wavefront .obj loader which also has the capability to create a bounding box from obj files.

This is mostly of use to people who want to write their own 3D game in Pyglet and get up and running quickly.
