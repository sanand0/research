from pathlib import Path
import FreeCAD as App
src=Path("results/freecad-parametric-smoke.FCStd").resolve()
out=Path("results/freecad-parametric-smoke-edited.FCStd").resolve()
doc=App.openDocument(str(src))
pad=doc.getObject("Pad")
print("before",pad.Length.Value,doc.getObject("Body").Tip.Shape.Volume)
pad.Length=15
doc.recompute()
body=doc.getObject("Body")
assert body.Tip.Shape.isValid() and len(body.Tip.Shape.Solids)==1
print("after",pad.Length.Value,body.Tip.Shape.Volume)
bb=body.Tip.Shape.BoundBox
print("bbox",bb.XLength,bb.YLength,bb.ZLength)
doc.saveAs(str(out))
App.closeDocument(doc.Name)
