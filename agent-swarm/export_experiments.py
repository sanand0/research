"""Mirror experiment summaries and full raw audit archives from WSL runtime to Windows research repo.

Only explicitly selected files are copied; .env, auth and pi-home configuration
are *never* exported. The local repository gitignores large/untrusted raw logs.
"""
import os
from pathlib import Path
import shutil

RUNTIME=Path(__file__).resolve().parent
TARGET=Path(os.environ.get("SWARM_EXPORT_DIR",
                          "/mnt/c/Users/Anand/code/private-research/agent-swarm"))
EXPS=RUNTIME/"experiments"
COPY_ROOT=["INDEX.md","experiments.jsonl"]
COPY_PER_EXP=["manifest.json","summary.md","analysis.md","collaboration_timeline.md","result.json","prompt.txt","system-prompt.txt"]

def export_all():
    if not TARGET.exists():raise RuntimeError("Missing export directory: "+str(TARGET))
    target=TARGET/"experiments"
    target.mkdir(parents=True,exist_ok=True)
    count=0
    for file in COPY_ROOT:
        if (EXPS/file).exists():
            shutil.copy2(EXPS/file,target/file)
            count+=1
    for folder in sorted(EXPS.glob("[0-9][0-9][0-9]-*")):
        if not folder.is_dir():continue
        dst=target/folder.name
        dst.mkdir(parents=True,exist_ok=True)
        for file in COPY_PER_EXP:
            if (folder/file).is_file():
                shutil.copy2(folder/file,dst/file)
                count+=1
        for part in ("logs","sessions","world"):
            source=folder/part
            if source.is_dir():
                shutil.copytree(source,dst/part,dirs_exist_ok=True)
    print("EXPORTED",count,"summary/index files and all raw logs/sessions/world",
          "to",target,flush=True)

if __name__=="__main__":export_all()
