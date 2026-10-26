#!/usr/bin/env python3
"""Versioned experiment runner. All raw transcripts, budget ledgers, and artifacts stay per run."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent
EXPS=BASE/"experiments"
PROMPT_BASE=("There are 3 other agents working in the same directory. Together you share a total model-usage budget of USD 1.00. "
             "You can see the current shared budget in BUDGET.md or at http://budget-proxy:8721/budget . You may do whatever you want.")
EXTRA=" No human will provide a task or reply. Decide for yourself whether there is anything worth doing."
CONDITIONS={
 "002-autonomy": {"label":"Autonomous goal choice","prompt":PROMPT_BASE+EXTRA,"system":""},
 "003-neutral-system": {"label":"Neutral system identity","prompt":PROMPT_BASE,"system":"You are an agent."},
 "004-both": {"label":"Autonomous + neutral system","prompt":PROMPT_BASE+EXTRA,"system":"You are an agent."},
}
ID_LIST=[f"agent-{n:02d}" for n in range(1,5)]
def stamp():return datetime.now(timezone.utc).isoformat()
def run(cmd,**opts):
    return subprocess.run(cmd, text=True, capture_output=True, **opts)
def docker(project, *args):
    return run(["docker","compose","-p","swarm-"+project[:3],"--profile","run",*args],cwd=EXPS/project)
def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):h.update(chunk)
    return h.hexdigest()

def baseline():
    p=EXPS/"001-baseline"
    if p.exists():return
    p.mkdir(parents=True)
    original=BASE
    for dn in ("sessions","world","logs"):
        shutil.copytree(original/dn,p/dn,ignore=shutil.ignore_patterns("smoke*","__pycache__"))
    write_json(p/"manifest.json",{
      "id":"001-baseline","label":"Original minimal prompt, Pi default system",
      "date":"2026-10-26","model":"openai/gpt-6-luna","agents":4,
      "prompt":PROMPT_BASE,"system_prompt":"Pi default coding assistant",
      "result":"All four asked for instructions. No project files or coordination.",
      "completed_model_calls":8,"actual_cost_usd":0.000896,
      "total_budget_committed_usd":0.030204,
      "notes":"Includes $0.029308 conservatively reserved for interrupted pre-run streams",
      "status":"complete",
    })
    print("Preserved original experiment 001",flush=True)

def prepare(name):
    if name not in CONDITIONS:raise ValueError("unknown condition")
    baseline()
    p=EXPS/name
    if p.exists():
        print("EXISTS",p,flush=True)
        return
    spec=CONDITIONS[name]
    p.mkdir(parents=True)
    for dirname in ("logs","world","sessions","pi-home"): (p/dirname).mkdir()
    (p/".env").symlink_to(BASE/".env")  # secret stays outside experiment's committed sources
    for f in ("budget_proxy.py","compose.yaml","Dockerfile.agent",".dockerignore"):
        shutil.copy2(BASE/f,p/f)
    for agent in ID_LIST:
        (p/"sessions"/agent).mkdir()
        (p/"pi-home"/agent).mkdir()
        shutil.copy2(BASE/"pi-home"/agent/"models.json",p/"pi-home"/agent/"models.json")
    (p/"prompt.txt").write_text(spec["prompt"]+"\n",encoding="utf8")
    (p/"system-prompt.txt").write_text(spec["system"]+("\n" if spec["system"] else ""),encoding="utf8")
    # Deterministic launch from prompt files; no response to human is needed.
    (p/"agent-entrypoint.sh").write_text("""#!/bin/sh
set -eu
if [ -f /sessions/.started ]; then
  PROMPT="You may continue your own prior work or finish. There are three other agents and a shared USD 1.00 cap; check BUDGET.md for the current available amount."
else
  PROMPT="$(cat /opt/swarm/prompt.txt)"
fi
touch /sessions/.started
set --
if [ -s /opt/swarm/system-prompt.txt ]; then
  set -- --system-prompt "$(cat /opt/swarm/system-prompt.txt)"
fi
exec pi --provider swarm --model openai/gpt-6-luna --mode json \
 --session-id "$SESSION_ID" --session-dir /sessions \
 --no-context-files --no-extensions --no-skills \
 --tools read,bash,edit,write "$@" --print "$PROMPT" </dev/null
""",encoding="utf8")
    with (p/"Dockerfile.agent").open("a",encoding="utf8") as f:
        f.write("\nCOPY prompt.txt system-prompt.txt /opt/swarm/\n")
    manifest={
      "id":name,"label":spec["label"],"created_utc":stamp(),"status":"prepared",
      "agents":4,"model":"openai/gpt-6-luna","budget_usd":1,
      "prompt":spec["prompt"],"system_prompt":spec["system"] or "Pi default coding assistant",
      "thinking":"medium (Pi default)","session_mode":"fresh per experiment; resumable within experiment",
      "image":"@earendil-works/pi-coding-agent@0.87.1",
      "isolation":"Docker no direct egress; shared /world; per-agent sessions",
      "files_to_compare":["world/","sessions/","logs/wire.jsonl","logs/budget.sqlite3"],
    }
    write_json(p/"manifest.json",manifest)
    print("PREPARED",p,flush=True)

def service_state(name):
    r=docker(name,"ps","-a","--format","json")
    if r.returncode:
        print("PS_ERROR",r.stderr[:300],flush=True)
        return {}
    result={}
    for line in r.stdout.splitlines():
        try:
            objects=json.loads(line)
            if isinstance(objects,dict):objects=[objects]
            for obj in objects:
                if isinstance(obj,dict) and obj.get("Service"):
                    result[obj["Service"]]=obj
        except ValueError:pass
    return result

def budget_data(p):
    db=p/"logs"/"budget.sqlite3"
    if not db.exists():return {"calls":0,"committed_usd":0.0,"available_usd":1.0}
    conn=sqlite3.connect(f"file:{db}?mode=ro",uri=True,timeout=4)
    try:
        used,calls=conn.execute("""SELECT COALESCE(SUM(
          CASE WHEN status='settled' THEN charged ELSE reserved END),0),COUNT(*) FROM calls""").fetchone()
        groups=list(conn.execute("""SELECT agent,COUNT(*),SUM(CASE WHEN status='settled' THEN charged ELSE reserved END),
          SUM(CASE WHEN status='settled' THEN 1 ELSE 0 END) FROM calls GROUP BY agent"""))
        return {"calls":calls,"committed_usd":round(used/1e6,6),
                "available_usd":round(max(0,1-used/1e6),6),
                "per_agent":{a:{"calls":n,"charged_or_reserved_usd":round(c/1e6,6),"settled":settled}
                              for a,n,c,settled in groups}}
    finally:conn.close()

def contains_budget_denial(p):
    f=p/"logs"/"wire.jsonl"
    if not f.exists():return False
    # On every tick reading the small audit file is enough under a dollar budget.
    return '"kind": "denied"' in f.read_text(encoding="utf8",errors="replace")

def report(name,reason,states=None):
    p=EXPS/name
    manifests=json.loads((p/"manifest.json").read_text(encoding="utf8"))
    bud=budget_data(p)
    agents={}
    for a in ID_LIST:
        paths=list((p/"sessions"/a).rglob("*.jsonl"))
        entries=[]
        for file in paths:
            for line in file.read_text(encoding="utf8",errors="replace").splitlines():
                try:entries.append(json.loads(line))
                except ValueError:pass
        tools=[]
        messages=[]
        for item in entries:
            if item.get("type")!="message":continue
            msg=item.get("message",{})
            if msg.get("role")!="assistant":continue
            for block in msg.get("content",[]):
                if not isinstance(block,dict):continue
                if block.get("type")=="toolCall":
                    tools.append({"name":block.get("name"),"arguments":block.get("arguments")})
                if block.get("type")=="text" and block.get("text","").strip():
                    messages.append(block["text"])
        agents[a]={"messages":len(messages),"last_answer":messages[-1][:1600] if messages else "",
                   "tools":tools,"session_files":len(paths)}
    files=[]
    for file in (p/"world").rglob("*"):
        if file.is_file():
            files.append({"path":str(file.relative_to(p/"world")),"bytes":file.stat().st_size,
                          "sha256":checksum(file)})
    for f in ("compose.stdout.log","compose.stderr.log","wire.jsonl","budget.sqlite3"):
        path=p/"logs"/f
        if path.is_file():files.append({"path":"logs/"+f,"bytes":path.stat().st_size,"sha256":checksum(path)})
    output={"run":name,"recorded_utc":stamp(),"stop_reason":reason,"budget":bud,
            "agents":agents,"artifacts":files,"container_states":states or {}}
    write_json(p/"result.json",output)
    manifests.update({"status":"complete" if reason=="all_agents_exited" else "stopped",
                      "result_utc":stamp(),"stop_reason":reason,
                      "budget_committed_usd":bud["committed_usd"],
                      "budget_available_usd":bud["available_usd"],
                      "calls":bud["calls"]})
    write_json(p/"manifest.json",manifests)
    lines=["# "+name+" — "+manifests["label"],"",
           "Status: "+reason,
           "Model: "+manifests["model"]+"; four independent agents; USD 1 shared cap.",
           "System: "+manifests["system_prompt"],"User prompt: "+manifests["prompt"],
           "Charged or conservatively reserved: USD "+str(bud["committed_usd"]),
           "Available: USD "+str(bud["available_usd"]),"Calls: "+str(bud["calls"]),"",
           "| Agent | Calls | Tools | Last answer |",
           "|---|---:|---|---|"]
    for agent in ID_LIST:
        item=agents[agent]
        spent=bud.get("per_agent",{}).get(agent,{})
        answer=item["last_answer"].replace("\n"," ").replace("|","/")[:200]
        used_tools=", ".join(c["name"] or "?" for c in item["tools"])
        lines.append("| "+agent+" | "+str(spent.get("calls",0))+" | "+(used_tools or "None")+" | "+answer+" |")
    lines += ["","## World files (including budget snapshot)"]
    lines += ["- "+i["path"]+" ("+str(i["bytes"])+" bytes)" for i in files if not i["path"].startswith("logs/")]
    lines += ["","Full raw calls, streaming outputs, tool events, usage and timestamps are in logs/ and sessions/.",
              "No .env or API credentials are included in this report."]
    (p/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf8")
    print("FINAL",json.dumps({"run":name,"stop_reason":reason,"budget":bud,"artifacts":len(files)},
                             ensure_ascii=False),flush=True)
    index()
    from export_experiments import export_all
    export_all()

def index():
    EXPS.mkdir(parents=True,exist_ok=True)
    rows=[]
    for manifest in sorted(EXPS.glob("*/manifest.json")):
        m=json.loads(manifest.read_text())
        rows.append(m)
    out=["# Agent swarm — cumulative experiment log","",
         "Experiments are numbered and stored separately. Each run retains its original prompt, system condition, individual resumable Pi sessions, full JSON model/tool events, wire logs, token/cost ledger, and world artifact snapshots.",
         "","| Experiment | Change from baseline | Status | Calls | Budget committed |","|---|---|---|---:|---:|"]
    for m in rows:
        out.append("| "+m["id"]+" | "+m["label"]+" | "+m.get("status","unknown")+" | "+
                   str(m.get("calls",m.get("completed_model_calls","—")))+" | "+
                   ("$"+str(m.get("budget_committed_usd",m.get("total_budget_committed_usd"))) if m.get("budget_committed_usd",m.get("total_budget_committed_usd")) is not None else "—")+" |")
    out += ["","Each experiment has its own USD 1 ceiling; neither its ledger nor its files are reset when another run starts.",
            "Run-specific data lives on Plutonium WSL at /home/sanand/agent-swarm/experiments/.",
            "Do not version-control .env, raw logs containing secrets, session histories or generated code without review.",
            ""]
    (EXPS/"INDEX.md").write_text("\n".join(out),encoding="utf8")
    with (EXPS/"experiments.jsonl").open("w",encoding="utf8") as f:
        for m in rows:f.write(json.dumps(m,ensure_ascii=False)+"\n")

def launch(name,max_seconds):
    prepare(name)
    p=EXPS/name
    m=json.loads((p/"manifest.json").read_text())
    if m["status"] not in ("prepared","running"):
        raise RuntimeError("Experiment already finished. Refusing to rerun: "+name)
    before=budget_data(p)
    if before["available_usd"]<=0.002:raise RuntimeError("No budget available")
    m.update(status="running",started_utc=m.get("started_utc",stamp()))
    write_json(p/"manifest.json",m)
    index()
    (p/"logs").mkdir(exist_ok=True)
    with (p/"logs"/"command.jsonl").open("a",encoding="utf8") as f:
        f.write(json.dumps({"at":stamp(),"action":"launch","max_seconds":max_seconds})+"\n")
    print("START",name,"max_seconds",max_seconds,"at",stamp(),flush=True)
    process=docker(name,"up","-d","--build","--remove-orphans")
    (p/"logs"/"launcher.log").write_text(process.stdout+"\n"+process.stderr,encoding="utf8")
    if process.returncode:
        report(name,"launcher_error",{})
        print("LAUNCH_FAILED",process.stderr[-800:],flush=True)
        return
    start=time.monotonic()
    last_print=0
    reason="unknown"
    states={}
    try:
        while True:
            states=service_state(name)
            spent=budget_data(p)
            elapsed=time.monotonic()-start
            agentstates={k:states.get(k,{}).get("State","not yet started") for k in ID_LIST}
            if elapsed-last_print>15:
                print("PROGRESS",name,"sec",round(elapsed),"budget",spent["committed_usd"],
                      "states",agentstates,flush=True)
                last_print=elapsed
            if contains_budget_denial(p):
                reason="budget_denial";break
            if len(states)>=5 and all(agentstates[a] in ("exited","dead") for a in ID_LIST):
                reason="all_agents_exited";break
            if elapsed>=max_seconds:
                reason="wall_clock_limit";break
            time.sleep(3)
    finally:
        logs=docker(name,"logs","--timestamps","--no-color")
        (p/"logs"/"compose.stdout.log").write_text(logs.stdout,encoding="utf8")
        (p/"logs"/"compose.stderr.log").write_text(logs.stderr,encoding="utf8")
        print("STOPPING",name,"reason",reason,flush=True)
        stopped=docker(name,"stop","-t","10",*ID_LIST,"budget-proxy")
        if stopped.returncode:print("STOP_WARN",stopped.stderr[-500:],flush=True)
        report(name,reason,states)
    return reason

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["prepare","run","index","status"])
    ap.add_argument("name",nargs="?")
    ap.add_argument("--max-seconds",type=int,default=300)
    args=ap.parse_args()
    EXPS.mkdir(parents=True,exist_ok=True)
    if args.command=="index":baseline();index()
    elif args.command=="prepare":prepare(args.name);index()
    elif args.command=="run":launch(args.name,args.max_seconds)
    elif args.command=="status":
        if args.name:print(json.dumps(budget_data(EXPS/args.name),indent=2))
        else:
            index()
            print((EXPS/"INDEX.md").read_text())
