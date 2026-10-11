"""Inline story.json and app.js into template.html -> index.html."""
import sys
from pathlib import Path
here = Path(__file__).parent
html = (here / 'template.html').read_text()
data = (here / 'story.json').read_text().replace('</', '<\\/')   # keep </script> out of the JSON island
app = (here / 'app.js').read_text()
html = html.replace('__DATA__', data).replace('<script type="module" src="./app.js"></script>', f'<script type="module">\n{app}</script>')
Path(sys.argv[1]).write_text(html)
print(sys.argv[1], len(html))
