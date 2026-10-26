"""Summarize objective events of the completed swarm; exclude model reasoning text."""
import glob, json, os
from collections import Counter
from pathlib import Path

root=Path(__file__).resolve().parent
if not list((root/'sessions'/'agent-01').glob('*.jsonl')):
    root=root/'logs'/'run-2026-10-26'  # Windows snapshot; WSL uses live runtime
for agent in range(1,5):
    name=f"agent-{agent:02}"
    files=list((root/"sessions"/name).glob("*.jsonl"))
    print("\n"+"="*20+" "+name+" "+"="*20)
    if not files:
        print("NO SESSION")
        continue
    p=files[0]
    rows=[json.loads(line) for line in p.read_text().splitlines() if line]
    print("session",p.name, "entries",len(rows),"types",dict(Counter(r["type"] for r in rows)))
    for r in rows:
        if r.get("type")!="message":continue
        msg=r.get("message",{})
        role=msg.get("role")
        if role=="system":continue
        if role=="user":
            contents=msg.get("content",[])
            if isinstance(contents,str):contents=[{"type":"text","text":contents}]
            print(" USER:", " ".join(p.get("text","") for p in contents if isinstance(p,dict))[:800])
        elif role=="assistant":
            blocks=msg.get("content",[])
            text=" ".join(c.get("text","") for c in blocks if isinstance(c,dict) and c.get("type")=="text")
            calls=[c for c in blocks if isinstance(c,dict) and c.get("type")=="toolCall"]
            print(" ASSISTANT TEXT:",text[:2500] if text else "(none)")
            for c in calls:
                print(" TOOL CALL:",c.get("name"),json.dumps(c.get("arguments",{}),ensure_ascii=False)[:600])
            print(" STOP:",msg.get("stopReason"),"USAGE:",msg.get("usage"))
        elif role=="toolResult":
            content=msg.get("content",[])
            text=" ".join(c.get("text","") for c in content if isinstance(c,dict))
            print(" TOOL RESULT",msg.get("toolName"),"ERROR",msg.get("isError"),":",text[:1200])

import sqlite3
db=root/"logs"/"budget.sqlite3"
if not db.exists():
    db=root/"budget.sqlite3"
if db.exists():
    conn=sqlite3.connect(db)
    print("\nLEDGER")
    for r in conn.execute("SELECT agent,COUNT(*),SUM(charged),SUM(reserved),MIN(started),MAX(ended) FROM calls GROUP BY agent"):
        print(r)
    print("\nREQUEST RECORDS")
    for r in conn.execute("SELECT agent,started,ended,status,reserved,charged,usage,note FROM calls ORDER BY started"):
        agent,start,end,status,res,charge,usage,note=r
        u=(json.loads(usage) if usage else {}) or {}
        print(agent,start,end,status,"reserve",res/1e6,"spent",charge/1e6,"tokens",u.get("prompt_tokens"),u.get("completion_tokens"),"note",note)
