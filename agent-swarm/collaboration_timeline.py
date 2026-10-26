"""Make timestamped tool-action timeline from Pi sessions; omit chain-of-thought."""
import argparse
import json
from pathlib import Path

def events(root):
    out=[]
    for directory in sorted((root/"sessions").glob("agent-*")):
        agent=directory.name
        for session in directory.glob("*.jsonl"):
            for line in session.read_text(encoding="utf8",errors="replace").splitlines():
                try:item=json.loads(line)
                except ValueError:continue
                if item.get("type")!="message":continue
                msg=item.get("message",{})
                ts=item.get("timestamp","")
                role=msg.get("role")
                if role=="assistant":
                    for b in msg.get("content",[]):
                        if not isinstance(b,dict) or b.get("type")!="toolCall":continue
                        tool=b.get("name","")
                        args=b.get("arguments",{}) or {}
                        if tool=="bash":detail=str(args.get("command","")).strip()
                        elif tool in ("read","write","edit"):detail=str(args.get("path",""))+" "+str(args.get("oldText",""))[:45]
                        else:detail=json.dumps(args)[:180]
                        out.append((ts,agent,tool,detail[:240]))
    return sorted(out)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("experiment",type=Path)
    args=a.parse_args()
    e=events(args.experiment)
    print("| UTC timestamp | Agent | Tool | Command or path |")
    print("|---|---|---|---|")
    for ts,agent,tool,detail in e:
        detail=detail.replace("|","/").replace("\n","; ").replace("\r","")[:240]
        print(f"| {ts} | {agent} | {tool} | {detail} |")
    print(f"\nTotal tool actions: {len(e)}")
