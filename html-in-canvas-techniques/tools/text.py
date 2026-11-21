"""Visible text of body (no script/style)."""
import re, sys, pathlib, html
s = pathlib.Path(sys.argv[1]).read_text(errors="ignore")
s = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", s, flags=re.S|re.I)
s = re.sub(r"<br\s*/?>|</(p|h\d|li|div|section|tr|button|label)>", "\n", s, flags=re.I)
s = html.unescape(re.sub(r"<[^>]+>", " ", s))
print("\n".join(l for l in (re.sub(r"[ \t]+", " ", x).strip() for x in s.splitlines()) if l))
