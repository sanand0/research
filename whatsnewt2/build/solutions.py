"""Reference answers to every puzzle.

These are held as strings rather than as real code, because several of them are
syntax errors on any interpreter older than 3.15 -- which is rather the point.
Also serves as the walkthrough, for anyone who would rather read than play.
"""

SOLUTIONS = {
    'lazy-imports': '''\
lazy import json
lazy from pathlib import Path
''',

    'frozendict': '''\
pairs = [('lang', 'Python'), ('version', '3.15'), ('mood', 'lazy')]

SETTINGS = frozendict(pairs)
SHUFFLED = frozendict(reversed(pairs))

LEDGER = {SETTINGS: 'stamped first', SHUFFLED: 'stamped second'}
''',

    'sentinel': '''\
MISSING = sentinel('MISSING')


def lookup(mapping, key, default=MISSING):
    if key in mapping:
        return mapping[key]
    if default is MISSING:
        raise KeyError(key)
    return default
''',

    'unpacking': '''\
beds = [['fern', 'moss'], ['ivy'], ['thyme', 'sage', 'rue']]
labels = [{'fern': 'shade'}, {'ivy': 'climber'}, {'fern': 'damp shade'}]

plants = [*bed for bed in beds]
legend = {**label for label in labels}
''',

    'utf8': '''\
def save(path, text):
    with open(path, 'w') as stream:
        stream.write(text)


def load(path):
    with open(path) as stream:
        return stream.read()


def read_legacy_log(path):
    with open(path, encoding='locale') as stream:
        return stream.read()
''',

    'typeddict': '''\
from typing import TypedDict


class Movie(TypedDict, closed=True):
    name: str
    year: int


class Vigil(TypedDict, extra_items=float):
    station: str
''',

    'typeform': '''\
from typing import TypeForm


def parse[T](kind: TypeForm[T], raw: str) -> T:
    if kind is int:
        return int(raw)
    if kind is float:
        return float(raw)
    return raw
''',

    'disjoint-base': '''\
from typing import disjoint_base


@disjoint_base
class Reader:
    """Holds a buffer it only ever reads from."""


@disjoint_base
class Writer:
    """Holds a buffer it only ever writes to."""


class Both(Reader, Writer):
    """Neither one thing nor the other."""
''',

    'tachyon': '''\
python -m profiling.sampling attach 4242 --mode cpu -a --flamegraph
python -m profiling.sampling dump 99 -a --async-aware
python -m profiling.sampling run --mode gil bench.py
''',

    'take-bytes': '''\
def frames(buffer):
    found = []
    while (end := buffer.find(b'\\n')) != -1:
        found.append(buffer.take_bytes(end + 1))
    return found


def drain(buffer):
    return buffer.take_bytes()
''',

    'math-integer': '''\
from math.integer import comb, gcd, isqrt, lcm


def lattice_paths(rows, columns):
    return comb(rows + columns, rows)


def largest_square(area):
    return isqrt(area)


def beat(first, second):
    return lcm(first, second) // gcd(first, second)
''',

    'concurrent-tee': '''\
import threading


def harvest(source, workers=8):
    shared = threading.serialize_iterator(source)
    gathered = []
    lock = threading.Lock()

    def pick():
        for item in shared:
            with lock:
                gathered.append(item)

    threads = [threading.Thread(target=pick) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return gathered
''',

    'removals': '''\
import glob
import re
from datetime import datetime


def compiled(pattern):
    return re.compile(pattern)


def python_files(root):
    return sorted(glob.glob('*.py', root_dir=root))


def release_day(text):
    return datetime.strptime(text, '%Y-%m-%d')


def line_numbers(function):
    return list(function.__code__.co_lines())
''',

    'oracle': '''\
letters = ['a', 'b']
letters.append('c')

shout = 'hello'.upper()

counts = {}
counts['a'] = 1

point = [1, 2]
point.append(3)
''',

    'prefixmatch': '''\
import re

VERSION = r'\\d+\\.\\d+'


def starts_with_a_version(text):
    return re.prefixmatch(VERSION, text) is not None


def mentions_a_version(text):
    return re.search(VERSION, text) is not None
''',

    'start-file': '''\
# myapp.start
myapp.bootstrap:configure
''',

    'release': '''\
lazy import json

fragments = [
    {'lazy imports': 810, 'frozendict': 814},
    {'sentinel': 661, 'unpacking in comprehensions': 798},
    {'UTF-8 by default': 686, 'startup configuration files': 829},
]

FEATURES = frozendict({**fragment for fragment in fragments})
RELEASE_DATE = sentinel('UNRELEASED')
''',
}

SOLUTIONS['scriptorium'] = '''\
import unicodedata


def shorten(text, limit):
    """Cut text down to at most `limit` characters, as a person counts them."""
    clusters = list(unicodedata.iter_graphemes(text))
    if len(clusters) <= limit:
        return text
    return text[:clusters[limit].start]
'''
