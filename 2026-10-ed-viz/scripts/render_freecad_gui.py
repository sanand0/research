import os, time
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui

src=Path(os.environ["FCSTD"]).resolve()
out=Path(os.environ["PNG"]).resolve()
doc=App.openDocument(str(src))
Gui.activeDocument()
body=doc.getObject("Body")
for o in doc.Objects:
    try:
        o.ViewObject.Visibility=False
    except Exception:
        pass
body.ViewObject.Visibility=True
body.Tip.ViewObject.Visibility=True
Gui.updateGui()
view=Gui.activeDocument().activeView()
view.viewAxonometric()
view.fitAll()
Gui.updateGui()
time.sleep(0.5)
print("body visible",body.ViewObject.Visibility,"tip",body.Tip.ViewObject.Visibility)
print("camera",view.getCameraOrientation())
view.saveImage(str(out),900,700,"White")
print("saved",out,out.stat().st_size)
App.closeDocument(doc.Name)
Gui.getMainWindow().close()
