# /// script
# dependencies = ["websockets"]
# ///
"""Open URL in background tab, wheel-scroll in steps, screenshot each. Usage: scroll.py outdir url steps dy"""
import asyncio, json, sys, base64, urllib.request, websockets

async def main(out, url, steps, dy):
    v = json.load(urllib.request.urlopen("http://localhost:9222/json/version"))
    async with websockets.connect(v["webSocketDebuggerUrl"], max_size=None) as b:
        n = [0]
        async def call(method, params=None, sid=None):
            n[0] += 1; i = n[0]
            msg = {"id": i, "method": method, "params": params or {}}
            if sid: msg["sessionId"] = sid
            await b.send(json.dumps(msg))
            while True:
                m = json.loads(await b.recv())
                if m.get("id") == i: return m.get("result", m)
        tid = (await call("Target.createTarget", {"url": url, "background": True}))["targetId"]
        sid = (await call("Target.attachToTarget", {"targetId": tid, "flatten": True}))["sessionId"]
        await call("Emulation.setDeviceMetricsOverride", {"width": 1280, "height": 760, "deviceScaleFactor": 1, "mobile": False}, sid)
        await call("Emulation.setFocusEmulationEnabled", {"enabled": True}, sid)
        await asyncio.sleep(12)
        for k in range(steps):
            r = await call("Page.captureScreenshot", {"format": "jpeg", "quality": 60}, sid)
            open(f"{out}/explainer-{k:02d}.jpg", "wb").write(base64.b64decode(r["data"]))
            for _ in range(4):
                await call("Input.dispatchMouseEvent", {"type": "mouseWheel", "x": 640, "y": 420, "deltaX": 0, "deltaY": dy / 4}, sid)
                await asyncio.sleep(0.15)
            await asyncio.sleep(2.5)
        await call("Target.closeTarget", {"targetId": tid})
asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])))
