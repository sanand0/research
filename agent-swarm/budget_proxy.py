"""Budgeted OpenRouter API proxy for Pi. Loopback only; key never given to agents."""
import argparse
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json, os, sqlite3, threading, urllib.error, urllib.request, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL = "openai/gpt-6-luna"
PORT = 8721
MAX_OUT = 8192
RATE_IN, RATE_OUT = 0.0000001, 0.0000005
LIMIT = 1_000_000  # micro-USD, $1
def stamp(): return datetime.now(timezone.utc).isoformat()
def get_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    for line in (ROOT / ".env").read_text("utf-8-sig").splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip("'\"")
    raise RuntimeError("OPENROUTER_API_KEY missing from .env")

class Ledger:
    def __init__(self):
        (ROOT / "logs").mkdir(exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(ROOT/"logs"/"budget.sqlite3", check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS calls(
          id TEXT PRIMARY KEY, agent TEXT, started TEXT, ended TEXT,
          status TEXT, reserved INTEGER, charged INTEGER,
          usage TEXT, upstream_id TEXT, note TEXT)""")
        self.db.commit()
        self.snapshot()
    def log(self, kind, **kv):
        with self.lock, (ROOT/"logs"/"wire.jsonl").open("a",encoding="utf8") as f:
            f.write(json.dumps({"at":stamp(),"kind":kind,**kv},ensure_ascii=False)+"\n")
    def status(self):
        with self.lock:
            used,n,held=self.db.execute("""SELECT
              COALESCE(SUM(CASE WHEN status='settled' THEN charged ELSE reserved END),0),
              COUNT(*),COALESCE(SUM(status='reserved'),0) FROM calls""").fetchone()
            agents = {name: {"committed_usd":round(cost/1e6,6), "calls":count}
                      for name,cost,count in self.db.execute("""SELECT agent,
                       COALESCE(SUM(CASE WHEN status='settled' THEN charged ELSE reserved END),0),
                       COUNT(*) FROM calls GROUP BY agent""")}
            return dict(per_agent=agents,limit_usd=1.0, committed_usd=round(used/1e6,6),
                        available_usd=round(max(0,LIMIT-used)/1e6,6),
                        calls=n, unsettled=held, model=MODEL,
                        accounting="Provider usage.cost; token estimate fallback; missing usage reserves full worst case")
    def snapshot(self):
        x=self.status()
        (ROOT/"world").mkdir(exist_ok=True)
        tmp=ROOT/"world"/(".budget-"+uuid.uuid4().hex)
        tmp.write_text("# Shared budget\n\nLimit: USD 1.00\nCommitted (spent and reserved): USD "+str(x["committed_usd"])+
             "\nAvailable: USD "+str(x["available_usd"])+
             "\nCalls: "+str(x["calls"])+"\n\nLive status inside agent container: http://budget-proxy:8721/budget\n",
             encoding="utf8")
        os.replace(tmp,ROOT/"world"/"BUDGET.md")
    def reserve(self,rid,agent,amount,body):
        with self.lock:
            used=self.db.execute("""SELECT COALESCE(SUM(
              CASE WHEN status='settled' THEN charged ELSE reserved END),0) FROM calls""").fetchone()[0]
            if used+amount>LIMIT:
                self.log("denied",id=rid,agent=agent,requested_usd=amount/1e6)
                return False
            self.db.execute("INSERT INTO calls (id,agent,started,status,reserved,charged) VALUES (?,?,?,?,?,0)",
                            (rid,agent,stamp(),"reserved",amount))
            self.db.commit()
            self.log("request",id=rid,agent=agent,reserve_usd=amount/1e6,body=body)
            self.snapshot()
            return True
    def settle(self,rid,usage,upstream_id,note):
        with self.lock:
            row=self.db.execute("SELECT reserved FROM calls WHERE id=?",(rid,)).fetchone()
            if not row:return
            charge=row[0]
            source="worst_case"
            if isinstance(usage,dict):
                if isinstance(usage.get("cost"),(int,float)):
                    charge=max(0,round(usage["cost"]*1e6))
                    source="provider_cost"
                elif usage.get("prompt_tokens") is not None and usage.get("completion_tokens") is not None:
                    charge=max(0,round((usage["prompt_tokens"]*RATE_IN+usage["completion_tokens"]*RATE_OUT)*1e6))
                    source="token_estimate"
            self.db.execute("""UPDATE calls SET ended=?,status='settled',charged=?,
              usage=?,upstream_id=?,note=? WHERE id=?""",
              (stamp(),charge,json.dumps(usage),upstream_id,note,rid))
            self.db.commit()
            self.log("settled",id=rid,charged_usd=charge/1e6,reserved_usd=row[0]/1e6,
                     usage=usage,upstream_id=upstream_id,source=source,note=note)
            self.snapshot()

class Handler(BaseHTTPRequestHandler):
    protocol_version="HTTP/1.0"
    def log_message(self,*_):pass
    def reply(self,code,obj):
        data=json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if self.path=="/health":return self.reply(200,{"ok":True,"model":MODEL})
        if self.path=="/budget":return self.reply(200,self.server.ledger.status())
        return self.reply(404,{"error":"not found"})
    def do_POST(self):
        if self.path!="/v1/chat/completions":return self.reply(404,{"error":"unknown path"})
        try:
            length=int(self.headers.get("Content-Length",0))
            if length<1 or length>1000000:return self.reply(413,{"error":"body size"})
            raw=self.rfile.read(length)
            body=json.loads(raw)
            if body.get("model")!=MODEL:return self.reply(400,{"error":"model not allowed"})
            if b'"image_url"' in raw or b'data:image' in raw:
                return self.reply(400,{"error":"images disabled to bound cost"})
            body["max_tokens"]=min(MAX_OUT,int(body.get("max_tokens") or MAX_OUT))
            if "max_completion_tokens" in body:
                body["max_completion_tokens"]=min(MAX_OUT,int(body["max_completion_tokens"]))
            body["usage"]={"include":True}
            if body.get("stream"):body["stream_options"]={"include_usage":True}
        except (ValueError,TypeError):
            return self.reply(400,{"error":"invalid JSON or token limit"})
        # Over-reserve: UTF-8 JSON byte length * 2 + 8192 input tokens,
        # plus full output token allowance. Reserve 20% additional margin.
        n_in=length*2+8192
        reserved=max(1,int((n_in*RATE_IN+MAX_OUT*RATE_OUT)*1.2*1e6+0.9999))
        rid=str(uuid.uuid4())
        agent=self.headers.get("X-Swarm-Agent","unknown")[:80]
        ledger=self.server.ledger
        if not ledger.reserve(rid,agent,reserved,body):
            return self.reply(402,{"error":"Shared USD 1.00 budget exhausted","budget":ledger.status()})
        req=urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(body,ensure_ascii=False).encode(),
            headers={"Authorization":"Bearer "+self.server.api_key,
                     "Content-Type":"application/json",
                     "Accept-Encoding":"identity",
                     "X-Title":"Unguided agent swarm"},method="POST")
        usage=None
        upstream_id=None
        complete=False
        try:
            with urllib.request.urlopen(req,timeout=120) as response:
                streaming=bool(body.get("stream"))
                self.send_response(response.status)
                self.send_header("Content-Type","text/event-stream" if streaming else "application/json")
                self.send_header("Cache-Control","no-cache")
                self.end_headers()
                if streaming:
                    for line in response:
                        decoded=line.decode("utf-8","replace")
                        ledger.log("response_chunk",id=rid,chunk=decoded)
                        if decoded.startswith("data: "):
                            payload=decoded[6:].strip()
                            if payload=="[DONE]":complete=True
                            else:
                                try:
                                    ev=json.loads(payload)
                                    upstream_id=ev.get("id") or upstream_id
                                    usage=ev.get("usage") or usage
                                except ValueError:pass
                        self.wfile.write(line)
                        self.wfile.flush()
                else:
                    data=response.read()
                    ledger.log("response_body",id=rid,body=data.decode("utf-8","replace"))
                    obj=json.loads(data)
                    upstream_id=obj.get("id")
                    usage=obj.get("usage")
                    self.wfile.write(data)
                    complete=True
        except urllib.error.HTTPError as e:
            ledger.log("upstream_error",id=rid,status=e.code,body=e.read().decode("utf8","replace")[:1000])
            if e.code in (400,401,402,403,404,422,429):
                # These requests were rejected before a generation; no tokens billed.
                usage={"cost":0.0,"prompt_tokens":0,"completion_tokens":0}
            try:self.reply(e.code,{"error":"OpenRouter request failed","status":e.code})
            except (BrokenPipeError,ConnectionResetError):pass
        except Exception as e:
            ledger.log("network_error",id=rid,error=type(e).__name__,message=str(e)[:250])
        finally:
            ledger.settle(rid,usage,upstream_id,"complete" if complete else "error_or_interrupted")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["serve","status"])
    cmd=ap.parse_args().command
    ledger=Ledger()
    if cmd=="status":
        print(json.dumps(ledger.status(),indent=2))
        return
    server=ThreadingHTTPServer((os.environ.get("SWARM_LISTEN_HOST","127.0.0.1"),PORT),Handler)
    server.ledger=ledger
    server.api_key=get_key()
    print("Budget proxy listening on "+os.environ.get("SWARM_LISTEN_HOST","127.0.0.1")+":"+str(PORT),flush=True)
    try:server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=="__main__":main()
