# /// script
# dependencies = ["websockets"]
# ///
"""Open URLs in background CDP tabs, wait, screenshot (jpeg), close. Usage: shot.py outdir wait name=url..."""
import asyncio, json, sys, base64, urllib.request, websockets

async def cdp(ws, method, params=None, _id=[0]):
    _id[0] += 1; i = _id[0]
    await ws.send(json.dumps({"id": i, "method": method, "params": params or {}}))
    while True:
        m = json.loads(await ws.recv())
        if m.get("id") == i: return m.get("result", m)

async def one(name, url, out, wait):
    v = json.load(urllib.request.urlopen("http://localhost:9222/json/version"))
    async with websockets.connect(v["webSocketDebuggerUrl"], max_size=None) as b:
        t = await cdp(b, "Target.createTarget", {"url": url, "background": True, "newWindow": False})
        tid = t["targetId"]
        s = await cdp(b, "Target.attachToTarget", {"targetId": tid, "flatten": True})
        sid = s["sessionId"]
        async def sc(method, params=None, _n=[1000]):
            _n[0] += 1; i = _n[0]
            await b.send(json.dumps({"id": i, "sessionId": sid, "method": method, "params": params or {}}))
            while True:
                m = json.loads(await b.recv())
                if m.get("id") == i: return m.get("result", m)
        await sc("Emulation.setDeviceMetricsOverride", {"width": 1280, "height": 760, "deviceScaleFactor": 1, "mobile": False})
        await sc("Emulation.setFocusEmulationEnabled", {"enabled": True})
        await asyncio.sleep(wait)
        r = await sc("Page.captureScreenshot", {"format": "jpeg", "quality": 70})
        open(f"{out}/{name}.jpg", "wb").write(base64.b64decode(r["data"]))
        await cdp(b, "Target.closeTarget", {"targetId": tid})
        print("ok", name)

async def main():
    out, wait = sys.argv[1], float(sys.argv[2])
    await asyncio.gather(*(one(*a.split("=", 1), out, wait) for a in sys.argv[3:]))
asyncio.run(main())
