#!/usr/bin/env python3
# /// script
# dependencies = ["markdown"]
# ///
"""Package publishable Markdown posts and chart assets into data/publish/."""
from __future__ import annotations
from pathlib import Path
import shutil
import markdown

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis"
PUBLISH = ROOT / "data" / "publish"
POSTS = [
    {
        "slug": "kickoff-rules-laboratory",
        "title": "Kickoff is the NFL’s rules laboratory",
        "md": ANALYSIS / "kickoff_publish_ready_post.md",
        "assets": [
            ANALYSIS / "kickoff_return_touchback_rates.png",
            ANALYSIS / "kickoff_adjusted_return_rate_by_score_bucket.png",
        ],
    },
    {
        "slug": "replay-authority-map",
        "title": "The NFL is automating judgment at the edges first",
        "md": ANALYSIS / "replay_authority_post.md",
        "assets": [ANALYSIS / "replay_authority_map.png"],
    },
]

CSS = """
:root{--bg:#fff;--text:#162033;--muted:#667085;--line:#e4e7ec;--accent:#174ea6;}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.62 system-ui,-apple-system,Segoe UI,sans-serif;}
main{max-width:880px;margin:42px auto;padding:0 22px 80px;}
h1{font-size:42px;line-height:1.08;margin:0 0 24px;letter-spacing:-.03em}h2{margin-top:40px;font-size:25px}h3{margin-top:28px}
p{margin:16px 0}a{color:var(--accent)}img{max-width:100%;border:1px solid var(--line);border-radius:12px;margin:12px 0;background:#fff}
table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0;display:block;overflow:auto}th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{background:#f8fafc}.meta{color:var(--muted);font-size:14px;margin-bottom:26px}.note{border-left:4px solid var(--accent);padding:10px 16px;background:#f8fbff;color:#344054}
code{background:#f2f4f7;padding:1px 4px;border-radius:4px}pre{background:#101828;color:#f2f4f7;padding:14px;border-radius:10px;overflow:auto}pre code{background:transparent;padding:0}
"""

def md_to_html(md_text: str, title: str) -> str:
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])
    return f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title><style>{CSS}</style></head><body><main><div class='meta'>Generated from the NFL rules research pipeline.</div>{body}</main></body></html>"


def main() -> None:
    PUBLISH.mkdir(parents=True, exist_ok=True)
    links = []
    for post in POSTS:
        out_dir = PUBLISH / post["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        md_text = post["md"].read_text()
        (out_dir / "index.md").write_text(md_text)
        (out_dir / "index.html").write_text(md_to_html(md_text, post["title"]))
        for asset in post["assets"]:
            if asset.exists():
                shutil.copy2(asset, out_dir / asset.name)
        links.append(f"- [{post['title']}]({post['slug']}/index.html)")
    (PUBLISH / "index.html").write_text(md_to_html("# NFL Rules Research Posts\n\n" + "\n".join(links), "NFL Rules Research Posts"))
    print(PUBLISH)
    for p in PUBLISH.glob("*/*"):
        print(p)

if __name__ == "__main__":
    main()
