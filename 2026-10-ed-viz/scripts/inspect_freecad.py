import os
from pathlib import Path
import FreeCAD as App

path=Path(os.environ["FCSTD"]).resolve()
doc=App.openDocument(str(path))
print("FreeCAD", ".".join(App.Version()[:3]))
print("document", doc.Name, "objects", len(doc.Objects))
bodies=[o for o in doc.Objects if o.TypeId=="PartDesign::Body"]
print("bodies",len(bodies))
for body in bodies:
    group=list(body.Group)
    print("BODY",body.Name,"features",len(group),"tip",getattr(body.Tip,"Name",None))
    for i,obj in enumerate(group):
        shp=getattr(obj,"Shape",None)
        print(" ",i,obj.Name,obj.TypeId,"has_shape",bool(shp and not shp.isNull()))
    shape=body.Tip.Shape
    bb=shape.BoundBox
    print("solid_count",len(shape.Solids),"valid",shape.isValid(),"closed",shape.isClosed())
    print("volume",round(shape.Volume,6),"area",round(shape.Area,6))
    print("bbox",tuple(round(x,6) for x in (bb.XLength,bb.YLength,bb.ZLength)),
          "min",tuple(round(x,6) for x in (bb.XMin,bb.YMin,bb.ZMin)),
          "max",tuple(round(x,6) for x in (bb.XMax,bb.YMax,bb.ZMax)))
App.closeDocument(doc.Name)
