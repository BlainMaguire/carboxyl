import pyglet
from pyglet.gl import *
import math

class Box(object):
    def __init__(self, x1, y1, z1, x2, y2, z2, color=(0.14,1.0,1.0)):
        self.w, self.h, self.d = abs(x1-x2), abs(y1-y2), abs(z1-z2)
        self.w2, self.h2, self.d2 = self.w/2.0, self.h/2.0, self.d/2.0
        self.cx, self.cy, self.cz = (x1+x2)/2.0, (y1+y2)/2.0, (z1+z2)/2.0
        self.verts = [(x1,y1,z1),(x2,y1,z1),(x1,y2,z1),(x1,y1,z2),
                 (x2,y2,z1), (x1,y2,z2),(x2,y1,z2),(x2,y2,z2)]
        self.min_x, self.min_y, self.min_z = x1, y1, z1
        self.max_x, self.max_y, self.max_z = x2, y2, z2
        self.points = make_cuboid_points(x1,y1,z1,x2,y2,z2)
        self.color = color
    def draw(self):
        glColor3f(self.color[0],self.color[1],self.color[2])
        self.points.draw(GL_QUADS)
    def collide_sphere(self, cx, cy, cz, r):
        rcx, rcy, rcz = cx - self.cx, cy - self.cy, cz - self.cz
        
        if (rcx < -self.w2):
            bx = -self.w2
        elif (rcx > self.w2):
            bx = self.w2;
        else:
            bx = rcx
            
        if (rcy < -self.h2):
            by = -self.h2
        elif (rcy > self.h2):
            by = self.h2;
        else:
            by = rcy
            
        if (rcz < -self.d2):
            bz = -self.d2
        elif (rcz > self.d2):
            bz = self.d2;
        else:
            bz = rcz

        dx,dy,dz = rcx-bx, rcy-by, rcz-bz
        if ((dx*dx + dy*dy + dz*dz) < r*r):
            return True
        else:
            return False
    def collide_cylinder(self, tx, ty, tz, h, r):
        if self.min_y <= ty <= self.max_y or\
           self.min_y <= ty-h <= self.max_y:
               circle_dx = abs(tx - self.cx)
               circle_dz = abs(tz - self.cz)
            
               if (circle_dx > (self.w2 + r)):
                   return False
               if (circle_dz > (self.d2 + r)):
                   return False
            
               if (circle_dx <= (self.w2)):
                   return True
               if (circle_dz <= (self.d2)):
                   return True
            
               corner_dist_sq = (circle_dx - self.w2)**2 +\
                                (circle_dz - self.d2)**2
            
               return (corner_dist_sq <= (r**2))
        return False

def make_cuboid_points(x1, y1, z1, x2, y2, z2):
    w, h, d = abs(x1-x2)/2, abs(y1-y2)/2, abs(z1-z2)/2
    x, y, z = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
    return pyglet.graphics.vertex_list(24, ('v3f/static', [
        x-w,y+h,z-d, x-w,y+h,z+d, x+w,y+h,z+d, x+w,y+h,z-d, # top
        x-w,y-h,z-d, x+w,y-h,z-d, x+w,y-h,z+d, x-w,y-h,z+d, # bottom
        x-w,y-h,z-d, x-w,y-h,z+d, x-w,y+h,z+d, x-w,y+h,z-d, # left
        x+w,y-h,z+d, x+w,y-h,z-d, x+w,y+h,z-d, x+w,y+h,z+d, # right
        x-w,y-h,z+d, x+w,y-h,z+d, x+w,y+h,z+d, x-w,y+h,z+d, # front
        x+w,y-h,z-d, x-w,y-h,z-d, x-w,y+h,z-d, x+w,y+h,z-d, # back
    ]))

world = {}
cuboids = []

for x in range(-10,20,5):
    for z in range (-15, 25, 5):
        cuboids.append(Box(x, 0, z, x+2,6,z+2))
        
#cuboids.append(Box(-5, 6, -5, 5, 8, 5))
#cuboids.append(Box(0, 3, -8, 10, 5, 4, (0.5,1.0,0.5)))

humanoids = []

class Humanoid(object):
    height = 2
    width = height * 0.25
    strafe = [0, 0]
    position = (-20, height, 0)
    rotation = (180, 0)
    dy = 0
    flying = False
    quad = gluNewQuadric() 
    def get_sight_vector(self):
        x, y = self.rotation
        m = math.cos(math.radians(y))
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)
    def get_motion_vector(self):
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            if self.flying:
                m = math.cos(math.radians(y))
                dy = math.sin(math.radians(y))
                if self.strafe[1]:
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    dy *= -1
                dx = math.cos(math.radians(x + strafe)) * m
                dz = math.sin(math.radians(x + strafe)) * m
            else:
                dy = 0.0
                dx = math.cos(math.radians(x + strafe))
                dz = math.sin(math.radians(x + strafe))
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)
    def update(self, dt):
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)
    def _update(self, dt):
        # walking
        speed = 15 if self.flying else 5
        d = dt * speed
        dx, dy, dz = self.get_motion_vector()
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            self.dy -= dt / 5
            self.dy = max(self.dy, -0.5)
            dy += self.dy
        # collisions
        x, y, z = self.position
        x, y, z = self.collide( self.position, (x + dx, y + dy, z + dz))
        self.position = (x, y, z)
    def draw(self):
        glColor3f(0.8,0.2,0.2)
        x, y, z = self.position
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(90, 1,0,0)
        gluCylinder(self.quad, self.width, self.width, self.height, 8, 8)
        glPopMatrix()
    def collide_humanoid(self, human):
        hx, hy, hz = human.position
        x, y, z = self.position
        if y-self.height <= hy <= y or\
           y-self.height <= hy-human.height <= y:
            if math.sqrt((x-hx)**2+(z-hz)**2) <= (self.width+human.width):
                return True
        return False
    def collide(self, old_pos, new_pos, pad=height*0.25):
        #this would need something like space partitioning
        #if there are a large number of entities.
        p = list(new_pos)
        if p[1] < 0+self.height:
            self.dy = 0
            p[1] = old_pos[1]
            
        for cuboid in cuboids:
            if cuboid.collide_cylinder(old_pos[0], p[1], old_pos[2], self.height, pad):
                self.dy=0
                if (p[1] - old_pos[1] > 0):
                    p[1] = old_pos[1] - 0.25
                else:
                    p[1] = old_pos[1]
                break
        for cuboid in cuboids:
            if cuboid.collide_cylinder(p[0], old_pos[1], old_pos[2], self.height, pad):
                p[0] = old_pos[0]
                break
        for cuboid in cuboids:
            if cuboid.collide_cylinder(old_pos[0], old_pos[1], p[2], self.height, pad):
                p[2] = old_pos[2]
                break
     
        self.position = (p[0], old_pos[1], old_pos[2])
        for humanoid in humanoids:
            if not humanoid is self:
                if self.collide_humanoid(humanoid):
                    p[0] = old_pos[0]
     
        self.position = (old_pos[0], p[1], old_pos[2])           
        for humanoid in humanoids:
            if not humanoid is self:
                if self.collide_humanoid(humanoid):
                    self.dy=0
                    if (p[1] - old_pos[1] > 0):
                        p[1] = old_pos[1] - 0.25
                    else:
                        p[1] = old_pos[1]
                        break
                    
        self.position = (old_pos[0], old_pos[1], p[2])
        for humanoid in humanoids:
            if not humanoid is self:
                if self.collide_humanoid(humanoid):
                    p[2] = old_pos[2]
        return tuple(p)
        
humanoids.append(Humanoid())
h2 = Humanoid()
h2.position = (-11, Humanoid.height,-6)
humanoids.append(h2)
