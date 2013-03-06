import pyglet
import math
import sys
from pyglet.gl import *
from pyglet.window import key
from entities import *
import ctypes

world = {}

def cube_vertices(x, y, z, n):
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n, # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n, # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n, # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n, # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n, # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n, # back
    ]

#for display purposes
def init_cubes():
	points = []
	dim_range = range(-60,61,20)
	for x in dim_range:
		for y in dim_range:
			for z in dim_range:
				points.extend(cube_vertices(x,y,z,0.25))
				
				
	return pyglet.graphics.vertex_list(24*7*7*7, ('v3f/static', points))

cubes = init_cubes() 

def normalize(position):
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.exclusive = True
        self.flying = False
        self.sector = None
        self.reticle = None

        self.label = pyglet.text.Label('', font_name='Arial', font_size=24, 
            x=200, y=self.height - 100, anchor_x='left', anchor_y='top', 
            color=(64, 0, 0, 255))

        pyglet.clock.schedule_interval(self.update, 1.0 / 60)
    def set_exclusive_mouse(self, exclusive):
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        return
        x, y, z = humanoids[0].position
        dx, dy, dz = humanoids[0].get_sight_vector()
        d = scroll_y * 10
        self.position = (x + dx * d, y + dy * d, z + dz * d)
    def on_mouse_press(self, x, y, button, modifiers):
        if self.exclusive:
            vector = humanoids[0].get_sight_vector()
            if button == pyglet.window.mouse.LEFT:
                pass
        else:
            self.set_exclusive_mouse(True)
    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            m = 0.5
            x, y = humanoids[0].rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            humanoids[0].rotation = (x, y)
    def update(self, dt):
        humanoids[0].update(dt)
    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            humanoids[0].strafe[0] -= 1
        elif symbol == key.S:
            humanoids[0].strafe[0] += 1
        elif symbol == key.A:
            humanoids[0].strafe[1] -= 1
        elif symbol == key.D:
            humanoids[0].strafe[1] += 1
        elif symbol == key.SPACE:
            if humanoids[0].dy == 0:
                humanoids[0].dy = 0.05
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
            self.set_fullscreen(False)
        elif symbol == key.TAB:
            humanoids[0].flying = not humanoids[0].flying
    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            humanoids[0].strafe[0] += 1
        elif symbol == key.S:
            humanoids[0].strafe[0] -= 1
        elif symbol == key.A:
            humanoids[0].strafe[1] += 1
        elif symbol == key.D:
            humanoids[0].strafe[1] -= 1
    def on_resize(self, width, height):
        # label
        self.label.y = height - 10
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width / 2, self.height / 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )
    def set_2d(self):
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    def set_view(self):
        x, y = humanoids[0].rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = humanoids[0].position
        glTranslatef(-x, -y+0.125, -z)
    def set_3d(self):
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    def on_draw(self):
        self.clear()
        self.set_3d()
        self.set_view()
        glColor3f(0.5, 0.2, 0.2)
        for cuboid in cuboids:
            cuboid.draw()
        glColor3f(1.0,0.1,0.1)
        cubes.draw(GL_QUADS)
        for humanoid in humanoids[1:]:
            humanoid.draw()

        self.set_2d()
        self.draw_label()
    def draw_label(self):
        x, y, z = humanoids[0].position
        rotx,roty = humanoids[0].rotation
        winx, winy= self.get_location()
        self.label.text = '%02d (%.2f, %.2f, %.2f) (%.2f, %2f ) (%.f, %.f)' % (
            pyglet.clock.get_fps(), x, y, z, rotx,roty, winx, winy)

        self.label.draw()
    def draw_reticle(self):
        pass

def setup_fog():
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (ctypes.c_float * 4)(0.0, 0.4, 1.0, 1))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_DENSITY, 0.125)
    glFogf(GL_FOG_START, 85.0)
    glFogf(GL_FOG_END, 120.0)

def setup():
    glClearColor(0.0, 0.4, 1.0, 1)
    glEnable(GL_CULL_FACE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    setup_fog()

def main():
    window = Window(width=1024, height=800, caption='Mimesis', resizable=True)
    window.set_exclusive_mouse(True)
    window.set_fullscreen(True)
    setup()
    pyglet.app.run()

if __name__ == '__main__':
    main()
