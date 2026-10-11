"""Drive the real whatsnewt engine through a scripted playthrough and record everything."""

import json
import sys

from whatsnewt.challenges import PUZZLES
from whatsnewt.engine import COUNCIL, CURIOSITIES, Game
from whatsnewt.world import ITEMS, ROOMS, SIGILS


def lines(seq):
    return [{'t': line.text, 's': line.style, 'sp': [list(s) for s in line.spans]} for line in seq]


class Recorder:
    def __init__(self):
        self.game = Game()
        self.steps = []
        self.chapter = None
        self.chapters = []
        self.seen_rooms = set()

    def snapshot(self):
        g = self.game
        return {
            'room': g.room,
            'roomName': ROOMS[g.room].name,
            'score': g.score,
            'possible': g.possible(),
            'solved': len(g.solved),
            'puzzles': len(PUZZLES),
            'sigils': len(g.sigils),
            'sigilTotal': len(SIGILS),
            'rooms': len(g.visited),
            'roomTotal': len(ROOMS),
            'people': len(g.curiosities & set(COUNCIL)),
            'moves': g.moves,
            'finished': g.finished,
            'carrying': [{'name': ITEMS[k].name, 'sigil': ITEMS[k].sigil, 'key': k} for k in g.carrying],
            'curiosities': sorted(g.curiosities),
            'map': lines(g.map_lines(width=38)),
        }

    def chap(self, key, title, subtitle=''):
        self.chapter = key
        self.chapters.append({'key': key, 'title': title, 'subtitle': subtitle, 'step': len(self.steps)})

    def _room_details(self):
        """Every examinable noun in the current room, as the engine answers it right now."""
        g = self.game
        room = g.here
        nouns = {}
        for noun in room.details:
            nouns[noun] = lines(g._examine(noun).lines)
        for key in room.items:
            item = ITEMS[key]
            nouns.setdefault(item.name.removeprefix('a ').removeprefix('an ').removeprefix('the '),
                             [{'t': item.name, 's': 'title', 'sp': []},
                              *({'t': t, 's': 'body', 'sp': []} for t in item.description.split('\n'))])
        return nouns

    def _push(self, step):
        before = set(self.steps[-1]['state']['curiosities']) if self.steps else set()
        step['chapter'] = self.chapter
        step['state'] = self.snapshot()
        step['newEggs'] = sorted(set(step['state']['curiosities']) - before)
        if self.game.room not in self.seen_rooms:
            self.seen_rooms.add(self.game.room)
            step['details'] = self._room_details()
            step['detailsRoom'] = self.game.room
        self.steps.append(step)
        return step

    def say(self, cmd, think='', seed=None, **extra):
        if seed is not None:
            import random
            random.seed(seed)
        response = self.game.execute(cmd)
        out = lines(response.lines)
        step = {'kind': 'cmd', 'cmd': cmd, 'think': think, 'out': out, **extra}
        if response.puzzle is not None:
            step['opens'] = response.puzzle
        if response.ending:
            step['ending'] = True
        return self._push(step)

    def note(self, think, **extra):
        """A pure thinking beat, no command."""
        return self._push({'kind': 'note', 'think': think, **extra})

    def attempt(self, key, think, source=None, expect=None):
        puzzle = PUZZLES[key]
        source = puzzle.starter if source is None else source
        verdict, paid = self.game.submit(key, source)
        if expect is not None and verdict.solved != expect:
            sys.exit(f'{key}: expected solved={expect}, got {verdict.solved}: {verdict.message}')
        step = {
            'kind': 'puzzle', 'think': think, 'key': key,
            'code': source, 'lang': puzzle.language,
            'verdict': {'solved': verdict.solved, 'message': verdict.message, 'output': verdict.output},
            'paid': lines(paid),
        }
        return self._push(step)


def puzzle_catalog():
    return {
        key: {
            'title': p.title, 'citation': p.citation, 'briefing': p.briefing,
            'starter': p.starter, 'hints': list(p.hints), 'points': p.points,
            'reward': ITEMS[p.reward].name if p.reward else None,
            'rewardSigil': ITEMS[p.reward].sigil if p.reward else False,
            'lang': p.language, 'anchor': p.anchor, 'docs': [list(d) for d in p.docs],
        }
        for key, p in PUZZLES.items()
    }


def eggs_catalog():
    return {name: what for name, (what, _said) in CURIOSITIES.items()}


def dump(rec, path):
    data = {
        'steps': rec.steps,
        'chapters': rec.chapters,
        'puzzles': puzzle_catalog(),
        'eggs': eggs_catalog(),
        'council': list(COUNCIL),
        'rooms': {k: {'name': r.name, 'label': r.label, 'subtitle': r.subtitle} for k, r in ROOMS.items()},
    }
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    return data
