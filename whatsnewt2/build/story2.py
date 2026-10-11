"""The playthrough, part two: the Forge to the far side of the Gate."""

from solutions import SOLUTIONS


def part_two(r):
    S = SOLUTIONS

    # --------------------------------------------------------------- Forge
    r.chap('forge', 'The Forge', 'JIT · mimalloc · bytearray.take_bytes · lovely spam')
    r.say('east', "East from the Gardens into the Forge. *\"Hot, loud, and 8-9% faster than last year.\"*")
    r.say('take ingot', "A warm ingot. It's full of JIT and base64 trivia. Taking it.")
    r.say('examine anvil', "There's a bytearray on the anvil. What's on it?")
    r.note("*\"See the zero-copy anvil.\"* That's the puzzle's reward, which I don't have yet. A bytearray "
           "of... something. In a Python game, there's only one thing it could be made of.")
    r.say('spam', "It's a Python game in a building full of Monty Python references, so: `spam`.")
    r.note("*\"Lovely spam! Wonderful spam!\"* Curiosity found. The game is named whats**newt** too, so "
           "*\"she turned me into a newt\"* is sitting right there. Later.")
    r.say('solve', "The zero-copy anvil.")
    r.attempt('take-bytes',
              "`bytearray.take_bytes(n)` takes `n` bytes off the front **without copying** and removes them. "
              "With no argument it takes everything and leaves the buffer empty.",
              source=S['take-bytes'], expect=True)

    # ---------------------------------------------------------- Numerarium
    r.chap('numerarium', 'The Numerarium', 'PEP 791 · math.integer')
    r.say('down', "*\"Somebody is counting down there.\"* Down the stairs.")
    r.say('take crank', "A brass crank: `zlib.crc32_combine`. Souvenir.")
    r.say('solve', "")
    r.attempt('math-integer',
              "Avoiding the `math.` prefix should be enough... `from math import comb, gcd, isqrt, lcm`?",
              source="from math import comb, gcd, isqrt, lcm\n\n\ndef lattice_paths(rows, columns):\n"
                     "    return comb(rows + columns, rows)\n\n\ndef largest_square(area):\n"
                     "    return isqrt(area)\n\n\ndef beat(first, second):\n"
                     "    return lcm(first, second) // gcd(first, second)\n", expect=False)
    r.note("No, those are now *soft-deprecated aliases*. The integer functions have their own namespace: "
           "**`math.integer`**. Namespaces are one honking great idea.")
    r.attempt('math-integer', "", source=S['math-integer'], expect=True)
    r.say('up', "Back up.")

    # --------------------------------------------------------- Observatory
    r.chap('observatory', 'The Observatory', 'PEP 799 · Tachyon sampling profiler')
    r.say('north', "North to the Observatory. PEP 799: Tachyon, Pablo's sampling profiler.")
    r.say('examine telescopes', "The telescopes list every mode and output format. This is a cheat sheet, so I'll read it.")
    r.say('take wire', "That wire running floor to ceiling looks collectible.")
    r.note("*\"There is no wire here.\"* The *description* says wire, but the item has a different name. Classic "
           "parser adventure. `take` matches on the item's real name, so let me try the other noun.")
    r.say('take frame', "An *unbroken frame pointer*: PEP 831. CPython now builds with `-fno-omit-frame-pointer`, so profilers and debuggers can unwind native stacks.")
    r.say('solve', "This puzzle is a shell script, not Python: three `profiling.sampling` command lines.")
    r.attempt('tachyon',
              "1: `attach 4242 --mode cpu --flamegraph`. 2: `dump 99 -a --async-aware`. 3: `run --mode gil bench.py`, "
              "since `run` profiles from the very first bytecode.",
              source="python -m profiling.sampling attach 4242 --mode cpu --flamegraph\n"
                     "python -m profiling.sampling dump 99 -a --async-aware\n"
                     "python -m profiling.sampling run --mode gil bench.py\n", expect=False)
    r.note("*\"Case 1 says every thread, not just the main one: -a.\"* I read \"every thread\" and then forgot "
           "it. Fair cop.")
    r.attempt('tachyon', "Adding `-a` to case 1.", source=S['tachyon'], expect=True)
    r.note("**Sigil: the Tachyon lens.** That makes five so far: lantern, seal, key, prism, lens. The last one is "
           "the UTF-8 compass, in the Tower of Babel, and I haven't explored the east side at all yet.")

    # --------------------------------------------------------------- Babel
    r.chap('babel', 'The Encoding Tower of Babel', 'PEP 686 · UTF-8 by default')
    r.say('south', "South back through the Forge, then south again into Babel.")
    r.say('south', "")
    r.say('take tablet', "A script tablet: `unicodedata.block()`.")
    r.say('solve', "")
    r.attempt('utf8',
              "In 3.15 text I/O is UTF-8 everywhere, so I can delete all three `encoding=` arguments!",
              source="def save(path, text):\n    with open(path, 'w') as stream:\n        stream.write(text)\n\n\n"
                     "def load(path):\n    with open(path) as stream:\n        return stream.read()\n\n\n"
                     "def read_legacy_log(path):\n    with open(path) as stream:\n        return stream.read()\n",
              expect=False)
    r.note("Too eager. The legacy log really was written in the machine's locale encoding, and deleting the "
           "argument would make 3.15 decode it as UTF-8. `encoding='locale'` (available since 3.10) asks for the "
           "locale explicitly.")
    r.attempt('utf8', "Two encodings deleted, one spelled `'locale'`.", source=S['utf8'], expect=True)
    r.note("**All six sigils.** The Gate will open. But there are still puzzles upstairs and to the south, and "
           "I want the perfect score.")

    # --------------------------------------------------------- Scriptorium
    r.chap('scriptorium', 'The Scriptorium', 'Unicode 17 · unicodedata.iter_graphemes')
    r.say('up', "Up to where the scribes copy text by hand.")
    r.say('newt', "This game is called whats*newt*, so I owe it this one.")
    r.say('solve', "")
    r.attempt('scriptorium',
              "Running the code-point version first to see how badly it mangles things.",
              source=None, expect=False)
    r.attempt('scriptorium',
              "`iter_graphemes` yields **Segments** with `.start`/`.end` offsets. Count them, and if they don't fit, "
              "cut the original string at the start of segment `limit`. That never splits a family emoji or an accent.",
              source=S['scriptorium'], expect=True)
    r.say('down', "")

    # ----------------------------------------------------------------- Weir
    r.chap('weir', 'The Threading Weir', 'serialize_iterator & friends')
    r.say('south', "South of Babel: the Threading Weir, the last unexplored room.")
    r.say('examine shuttle', "The shuttle lists three new threading names. They are *not* interchangeable.")
    r.say('solve', "")
    r.attempt('concurrent-tee',
              "Eight threads pulling from one generator. I already have an iterator, so `serialize_iterator`. "
              "I wrap it **once**, before the threads start.",
              source=S['concurrent-tee'], expect=True)
    r.say('score', "Let's check the score before the finale.")
    r.say('secrets', "And the curiosity count...")
    r.note("**10 of 11.** I've said xyzzy, plugh, newt, spam and all six people. What's missing? It's a Python "
           "game, and the most famous easter egg in Python is `import this`, the Zen...")
    r.say('zen', "`zen`", seed=16)
    r.note("A random line of the Zen, read out of the interpreter's own copy of `this` (which is stored "
           "ROT13-encoded). Six of the nineteen lines carry a 3.15 footnote, and this one points at "
           "`re.prefixmatch`. Type `zen` again and you'll get a different line. **11 of 11 curiosities.**")

    # ----------------------------------------------------------------- Gate
    r.chap('gate', 'The Release Gate', 'The final manifest')
    r.say('jump gate', "Time to teleport. The Gate is unvisited, so this should fail...")
    r.say('jump loop', "...but the Great Loop works. Rooms answer to their map label too.")
    r.say('north', "North. Six sigils in hand.")
    r.say('examine calendar', "The release calendar is computed from today's date.")
    r.say('solve', "The Release Manifest, worth 40 points. Everything at once.")
    r.attempt('release',
              "`lazy import json`, a dict comprehension that unpacks, and `sentinel('UNRELEASED')`...",
              source="lazy import json\n\nfragments = [\n    {'lazy imports': 810, 'frozendict': 814},\n"
                     "    {'sentinel': 661, 'unpacking in comprehensions': 798},\n"
                     "    {'UTF-8 by default': 686, 'startup configuration files': 829},\n]\n\n"
                     "FEATURES = {**fragment for fragment in fragments}\nRELEASE_DATE = sentinel('UNRELEASED')\n",
              expect=False)
    r.note("*\"A manifest that can still be edited is not a manifest.\"* I forgot the `frozendict` wrapper.")
    r.attempt('release', "`frozendict({**fragment for fragment in fragments})`. Signing.", source=S['release'], expect=True)
    r.say('look', "The room has changed.")
    r.say('secrets', "Now that the game is won, `secrets` lists everything instead of saying *\"That would be telling\"*.")
    r.say('score', "")

    # --------------------------------------------------------------- Ending
    r.chap('ending', 'October', 'Through the gate')
    r.say('north', "Every puzzle, every souvenir, every curiosity. Nothing to warn me about. North, into October.")
    r.note("**375 / 375.** 18 puzzles, 6 sigils, 15 rooms, 8 souvenirs, 11 curiosities, and 0 hints bought.\n\n"
           "What I'll remember: the checker reads *how* you solved each puzzle, not just whether the output is "
           "right, so a nested `for` loop that happens to flatten correctly still fails. And the best easter egg "
           "is the six people. The game never names them; you're expected to know who built 3.15.")
