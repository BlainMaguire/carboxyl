import pyglet
import data
from vector3 import *
from matrix import *
from constants import *

def load_mtl(name):
    file = data.load_file('models/' + name)
    mtl = {}
    name = None
    for line in file:
        line = line.strip()
        if not line or line[0] == '#': continue
        tokens = line.split()
        cmd = tokens.pop(0)
        if cmd == 'newmtl':
            name = tokens[0]
        elif cmd == 'Kd':
            mtl[name] = tuple(int(float(x) * 255) for x in tokens)
    return mtl
    
_obj_cache = {}
def load_obj_data(name):
    #if name in _obj_cache:
    #    return _obj_cache[name]
    file = data.load_file('models/' + name)
    vertices = []
    faces = []
    mtl = {}
    rot = rx(90) * 1 #reflect_x
    color = (127, 127, 127)
    for line in file:
        line = line.strip()
        if not line or line[0] == '#': continue
        tokens = line.split()
        cmd = tokens.pop(0)
        if cmd == 'v':
            vertices.append(rot(v3(float(x) for x in tokens)))
        elif cmd == 'f':
            faces.append((tuple(int(x.split('/')[0]) for x in tokens), color))
        elif cmd == 'mtllib':
            mtl = load_mtl(tokens[0])
        elif cmd == 'usemtl':
            color = mtl[tokens[0]]
    xs, ys, zs = zip(*vertices)
    bbox = Box(min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
    vdata = []
    cdata = []
    for face, color in faces:
        vxs = [vertices[n-1] for n in face]
        for i in xrange(len(vxs) - 2):
            vdata.extend(vxs[0])
            cdata.extend(color)
            vdata.extend(vxs[i+2])
            cdata.extend(color)
            vdata.extend(vxs[i+1])
            cdata.extend(color)
    #if DEBUG:
    #    print name, len(vdata) // 9
    return vdata, cdata, bbox

def load_obj(name):
    vdata, cdata, _ = load_obj_data(name)
    return pyglet.graphics.vertex_list(len(vdata) // 3, ('v3f', vdata), ('c3B', cdata))
