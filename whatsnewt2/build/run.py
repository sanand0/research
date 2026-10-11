import os, sys, tempfile
os.environ['XDG_STATE_HOME'] = tempfile.mkdtemp()   # keep autosaves out of the real state dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver import Recorder, dump
from story1 import part_one
from story2 import part_two
r = Recorder()
part_one(r); part_two(r)
data = dump(r, sys.argv[1])
last = data['steps'][-1]['state']
print(len(data['steps']), 'steps', last['score'], '/', last['possible'], 'eggs', len(last['curiosities']), 'room', last['room'], 'finished', last['finished'])
