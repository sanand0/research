"""Drop comment lines shared by 3+ notes files (boilerplate); write *.u.txt."""
import pathlib, collections, sys
d = pathlib.Path(sys.argv[1]); files = sorted(d.glob("*.txt")); files = [f for f in files if not f.name.endswith(".u.txt")]
cnt = collections.Counter(l for f in files for l in set(f.read_text().splitlines()))
for f in files:
    keep = [l[:500] for l in f.read_text().splitlines() if cnt[l] < 3]
    f.with_suffix(".u.txt").write_text("\n".join(keep))
