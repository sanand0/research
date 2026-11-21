"""Extract comments + visible text from cleaned artifact HTML."""
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text(errors="ignore")
out = []
# block comments and HTML comments
for m in re.finditer(r"/\*(.*?)\*/|<!--(.*?)-->", src, re.S):
    t = (m.group(1) or m.group(2) or "").strip()
    if len(t) > 25: out.append("/* " + re.sub(r"\n\s*\*?\s*", " ", t) + " */")
# line comments (skip URLs)
for m in re.finditer(r"(?<![:\"'\\])//\s?([^\n]{25,})", src):
    out.append("// " + m.group(1).strip())
print("\n".join(dict.fromkeys(out)))
