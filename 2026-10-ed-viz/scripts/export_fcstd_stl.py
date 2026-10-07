import os
from pathlib import Path
import FreeCAD as App
import Mesh

src=Path(os.environ["FCSTD"]).resolve()
out=Path(os.environ["STL"]).resolve()
doc=App.openDocument(str(src))
bodies=[o for o in doc.Objects if o.TypeId=="PartDesign::Body"]
assert len(bodies)==1, f"expected one Body, got {len(bodies)}"
body=bodies[0]
assert body.Tip.Shape.isValid() and len(body.Tip.Shape.Solids)==1
Mesh.export([body.Tip],str(out))
print("saved",out,out.stat().st_size)
App.closeDocument(doc.Name)
