import os
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui

src=Path(os.environ["FCSTD"]).resolve()
outdir=Path(os.environ.get("OUTDIR","results/views")).resolve()
outdir.mkdir(parents=True,exist_ok=True)
doc=App.openDocument(str(src))
view=Gui.activeDocument().activeView()
views={
    "iso": view.viewAxonometric,
    "front": view.viewFront,
    "top": view.viewTop,
    "right": view.viewRight,
}
for name,setview in views.items():
    setview(); view.fitAll()
    path=outdir/f"{name}.png"
    view.saveImage(str(path),900,700,"White")
    print(name,path,path.stat().st_size)
App.closeDocument(doc.Name)
Gui.getMainWindow().close()
