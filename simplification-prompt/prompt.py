import sys

txt = open(sys.argv[1]).read()

for k, v in zip(sys.argv[2::2], sys.argv[3::2]):
    txt = txt.replace(f"{{{{{k[2:]}}}}}", open(v).read().strip())

print(txt)
