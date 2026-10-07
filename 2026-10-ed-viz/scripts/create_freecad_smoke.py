from pathlib import Path
import FreeCAD as App
import Part
import Sketcher

out=Path("results/freecad-parametric-smoke.FCStd").resolve()
doc=App.newDocument("ParametricSmoke")
body=doc.addObject("PartDesign::Body","Body")
sketch=doc.addObject("Sketcher::SketchObject","Sketch")
body.addObject(sketch)

pts=[(-20,-12.5),(20,-12.5),(20,12.5),(-20,12.5)]
for i in range(4):
    a=pts[i]; b=pts[(i+1)%4]
    sketch.addGeometry(Part.LineSegment(App.Vector(*a,0),App.Vector(*b,0)),False)

pad=body.newObject("PartDesign::Pad","Pad")
pad.Profile=sketch
pad.Length=10
doc.recompute()
assert len(body.Tip.Shape.Solids)==1
assert body.Tip.Shape.isValid()
doc.saveAs(str(out))
print("saved",out)
print("features",[(o.Name,o.TypeId) for o in body.Group])
print("volume",body.Tip.Shape.Volume)
bb=body.Tip.Shape.BoundBox
print("bbox",bb.XLength,bb.YLength,bb.ZLength)
App.closeDocument(doc.Name)
