import FreeCAD as App
import Part, Sketcher
import math

DOC = App.newDocument('ForkedMountingBracket')
body = DOC.addObject('PartDesign::Body', 'Bracket')

def sketch(name, placement):
    s = DOC.addObject('Sketcher::SketchObject', name)
    body.addObject(s)
    s.Placement = placement
    return s

# Sketch coordinates are x and height; its normal points toward +Y.
front = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), -90))
# With this placement the second sketch coordinate corresponds to -Z.
def line(s, a, b):
    s.addGeometry(Part.LineSegment(App.Vector(a[0], -a[1], 0), App.Vector(b[0], -b[1], 0)), False)
def arc(s, a, m, b):
    s.addGeometry(Part.Arc(App.Vector(a[0], -a[1], 0), App.Vector(m[0], -m[1], 0), App.Vector(b[0], -b[1], 0)), False)
def pad(s, name, length):
    DOC.recompute()
    p = body.newObject('PartDesign::Pad', name)
    p.Profile = s
    p.Length = length
    s.Visibility = False
    DOC.recompute()
    return p

# Base plate and rear upright overlap by the full 10 mm base thickness.
s = sketch('BasePlan', App.Placement())
for a,b in zip([(-75,0),(75,0),(75,35),(-75,35)],[(75,0),(75,35),(-75,35),(-75,0)]):
    s.addGeometry(Part.LineSegment(App.Vector(a[0],a[1],0),App.Vector(b[0],b[1],0)),False)
base = pad(s, 'BasePlate_10mm', 10)

s = sketch('UprightOutline', front)
# Four R12 shoulder transitions, 138 wide lower web and 90 wide neck.
line(s,(-69,0),(69,0)); line(s,(69,0),(69,36))
r = 12 / math.sqrt(2)
arc(s,(69,36),(57+r,36+r),(57,48))
arc(s,(57,48),(57-r,60-r),(45,60))
line(s,(45,60),(45,88)); line(s,(45,88),(-45,88)); line(s,(-45,88),(-45,60))
arc(s,(-45,60),(-57+r,60-r),(-57,48))
arc(s,(-57,48),(-57-r,36+r),(-69,36))
line(s,(-69,36),(-69,0))
upright = pad(s, 'RearUpright_10mm', 10)
base.Visibility = False

# Supporting stem reaches the 35 mm mounting depth; the circular eye reaches 48.
s = sketch('StemOutline', front)
x = 17.99
zc = 66.82
pts = [(-x,35.13),(x,35.13),(x,zc),(-x,zc)]
for a,b in zip(pts,pts[1:]+pts[:1]): line(s,a,b)
stem = pad(s, 'StemSupport_35mm', 35)
upright.Visibility = False

s = sketch('EyeOuterProfile', front)
s.addGeometry(Part.Circle(App.Vector(0,-zc,0),App.Vector(0,0,1),x),False)
eye = pad(s, 'CircularEye_48mm', 48)
stem.Visibility = False

# Fork opening, through all of the 35 mm mounting base and rear upright.
s = sketch('ForkOpening', front)
pts = [(-25.195,-1),(25.195,-1),(25.195,25),(-25.195,25)]
for a,b in zip(pts,pts[1:]+pts[:1]): line(s,a,b)
DOC.recompute()
fork = body.newObject('PartDesign::Pocket','ForkClearance_50_39mm')
fork.Profile = s
fork.Length = 49
fork.Reversed = True
s.Visibility = False
DOC.recompute()
eye.Visibility = False

s = sketch('EyeBoreProfile', front)
s.addGeometry(Part.Circle(App.Vector(0,-66.82,0), App.Vector(0,0,1),10.15),False)
DOC.recompute()
bore = body.newObject('PartDesign::Pocket','EyeBore_20_3mm')
bore.Profile = s
bore.Length = 49
bore.Reversed = True
s.Visibility = False
DOC.recompute()
fork.Visibility = False

s = sketch('MountingHolesPlan', App.Placement(App.Vector(0,0,10),App.Rotation()))
for cx in [-63,63]:
    s.addGeometry(Part.Circle(App.Vector(cx,23,0),App.Vector(0,0,1),5),False)
DOC.recompute()
holes = body.newObject('PartDesign::Pocket','TwoMountingHoles_10mm')
holes.Profile = s
holes.Length = 10
s.Visibility = False
DOC.recompute()
bore.Visibility = False
holes.Visibility = True
body.Tip = holes
DOC.recompute()
shape = holes.Shape
bb = shape.BoundBox
print('BBOX: %.3f x %.3f x %.3f mm' % (bb.XLength, bb.YLength, bb.ZLength))
print('VOLUME: %.3f mm^3' % shape.Volume)
print('VALID:', shape.isValid())
print('SOLIDS:', len(shape.Solids))
for feature in [base,upright,stem,eye,fork,bore,holes]:
    print(feature.Name, feature.State, 'volume', feature.Shape.Volume)
assert shape.isValid() and len(shape.Solids)==1
assert abs(bb.XLength-150)<0.01 and abs(bb.YLength-48)<0.01 and abs(bb.ZLength-88)<0.01
DOC.recompute()
import os
DOC.saveAs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'answer.FCStd'))
