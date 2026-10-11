"""The playthrough, part one: Foyer to the Gardens."""

from solutions import SOLUTIONS


def part_one(r):
    S = SOLUTIONS

    # ------------------------------------------------------------------ Foyer
    r.chap('foyer', 'The Startup Foyer', 'PEP 829 · .start files · first magic words')
    r.say('look',
          "I just ran `uvx --python 3.15 whatsnewt`. A text adventure *about Python 3.15*, where every puzzle "
          "is checked by actually running my code on a 3.15 interpreter. The README swears there are easter eggs. "
          "Let's see where I woke up.")
    r.say('examine plaque',
          "A brass plaque. In old Infocom games you examine *everything*, so let's read it.")
    r.note("\"Contributed by **Barry Warsaw**.\" Barry also wrote this game. A real person's name, bolted "
           "to the wall of the very first room. I'm filing that away; it feels deliberate.")
    r.say('xyzzy',
          "Before anything else, the reflex every Colossal Cave player has: the magic word.")
    r.note("Ha! *\"lazy import fortune... It has not been imported yet.\"* That's a **curiosity** — and nothing "
           "in the help text mentions it. So the game listens for words it never advertises. Let me try the other one.")
    r.say('plugh',
          "Colossal Cave's *other* magic word.")
    r.say('jump',
          "One more classic adventure verb. In Zork, `jump` gets you a snarky reply.")
    r.note("**\"Nothing happens... yet.\"** That *yet* is doing a lot of work. `jump` is a real verb, and the "
           "door is only shut. Something unlocks it later. Noted.")
    r.say('secrets',
          "Does the game have a verb for these? Trying `secrets`...")
    r.note("*\"Some are words worth saying out loud, and some are **people** worth naming.\"* — 2 of 11. People "
           "worth naming... the plaque literally named one. Let's try it.")
    r.say('barry',
          "Saying the name on the plaque out loud: `barry`.")
    r.note("It worked, and a new line just appeared in the Progress pane: **People 1 / 6**. That line wasn't there "
           "a second ago, so showing it at all is the clue. Barry is **SCx6**, six terms on the Python "
           "*Steering Council*. Six people, then. I'll come back to this.\n\nNow, the actual puzzle.")
    r.say('examine lectern', "The lectern holds the blank `.start` file the puzzle is about.")
    r.say('take quill', "A rainbow quill on the floor. Souvenirs are worth 5 points each, so I'm taking everything that isn't nailed down.")
    r.say('solve', "Opening the puzzle editor. PEP 829: package startup configuration files.")
    r.attempt('start-file',
              "The old `.pth` hack was `import myapp.bootstrap; myapp.bootstrap.configure()`. My first instinct: "
              "just write the call, minus the `import`.",
              source='# myapp.start\nmyapp.bootstrap.configure()\n', expect=False)
    r.attempt('start-file',
              "Right, it's an *entry point specification*, the same `pkg.mod:callable` shape as "
              "`[project.scripts]`. No parentheses: `site` calls it for me, with no arguments. That's what "
              "makes it auditable. A `.start` file can only *name* a thing to run; it can't smuggle code in.",
              source=S['start-file'], expect=True)
    r.note("First puzzle down. The **start sash** isn't a sigil, so this was 15 points plus a souvenir. "
           "The Gate needs six sigils. Heading north into the Hall of Imports.")

    # -------------------------------------------------------------- Imports
    r.chap('imports', 'The Hall of Imports', 'PEP 810 · lazy imports · the council assembles')
    r.say('north', "North.")
    r.say('examine filter', "There's a filter and a rope. These descriptions double as documentation, so let me read both.")
    r.say('examine rope', "")
    r.note("Nice detail: `__lazy_modules__` only needs `__contains__`, so it can be any container. Now the puzzle.")
    r.say('solve', "")
    r.attempt('lazy-imports',
              "`lazy` is a soft keyword in front of the import statement. But I want to *see* it working, so I'll "
              "print the names to prove they're there...",
              source='lazy import json\nlazy from pathlib import Path\n\nprint(json, Path)\n', expect=False)
    r.note("Caught! *\"Something in your answer read the name and woke the proxy.\"* The checker inspects "
           "what got loaded. Printing `json` **reifies** the lazy import. That's the PEP 810 mental model: "
           "the name is a proxy until first use. The briefing even warned me.")
    r.attempt('lazy-imports', "Just the two statements this time, and no touching.", source=S['lazy-imports'], expect=True)
    r.note("**Sigil 1 of 6: the lazy lantern.**\n\nNow, those *people*. PEP 810 has several authors, two of whom "
           "are on the 2026 Steering Council: **Thomas Wouters** and **Pablo Galindo Salgado**. Test the theory.")
    r.say('thomas', "")
    r.say('pablo', "")
    r.note("People **3 / 6**. Thomas's line mentions he was *\"the release manager who shipped 3.13\"*, and the "
           "6th person might not be on the council at all. Who else is in the 2026 Steering Council? "
           "**Donghee Na** (co-author of PEP 814, frozendict) and **Savannah Ostrowski**.")
    r.say('donghee', "")
    r.say('savannah', "")
    r.note("**5 / 6.** That's the whole 2026 Steering Council. The sixth must be someone else who matters "
           "to 3.15. Thomas's hint about release managers points the way: the RM for 3.14 *and* 3.15 is "
           "**Hugo van Kemenade**.")
    r.say('hugo', "")
    r.note("**6 / 6.** Hugo is **RMx2**, and *\"edited the document you are inside\"*, meaning the "
           "What's New doc this whole game is built from. All six people are named. Remember "
           "\"Nothing happens... yet\"?")
    r.say('jump crypt', "Let's see whether `jump` works now...")
    r.note("*\"You have not been there yet.\"* So `jump` is **unlocked**, but it only goes to rooms I've already "
           "visited. Fair: it rewards playing, it doesn't skip the game. This will save a lot of backtracking later.")

    # --------------------------------------------------------------- Vault
    r.chap('vault', 'The Builtins Vault', 'PEP 814 frozendict · PEP 661 sentinel')
    r.say('west', "West to the Vault, which has two puzzles.")
    r.say('take badge', "An abi3t badge on the ledge. Into the pocket.")
    r.say('examine lock', "")
    r.say('solve A', "Puzzle A: frozendict. The starter says *run it as it stands* to see why a dict fails. Let's do exactly that.")
    r.attempt('frozendict', "Submitting the starter unchanged, the way the comment suggested.", source=None, expect=False)
    r.note("`unhashable type: 'dict'`, as expected. A mapping that's hashable, immutable, order-insensitive "
           "for equality but order-*preserving*: 3.15's new built-in `frozendict`. No import needed.")
    r.attempt('frozendict',
              "Both keys are cut from the same pairs, in opposite orders. They must hash equal, so the LEDGER "
              "collapses to one entry.", source=S['frozendict'], expect=True)
    r.say('solve B', "Puzzle B: sentinel. *The difference between nothing and None.*")
    r.attempt('sentinel',
              "The classic idiom is `MISSING = object()`. It's worked for twenty years...",
              source='MISSING = object()\n\n\ndef lookup(mapping, key, default=MISSING):\n'
                     '    if key in mapping:\n        return mapping[key]\n'
                     '    if default is MISSING:\n        raise KeyError(key)\n    return default\n',
              expect=False)
    r.note("*\"MISSING is still a object.\"* Right. PEP 661 finally gives sentinels a proper built-in: "
           "they have a readable repr, survive `copy` and `pickle` with their identity intact, and work in "
           "type expressions with `|`.")
    r.attempt('sentinel', "`sentinel('MISSING')` it is.", source=S['sentinel'], expect=True)

    # -------------------------------------------------------------- Typing
    r.chap('typing', 'The Typing Sanctum', 'PEP 728 · PEP 747 · PEP 800 (checked by pyrefly)')
    r.say('north', "North from the Vault into the Sanctum. Three puzzles here, and the README says a real type checker (pyrefly) judges some of them.")
    r.say('take glass', "A slice of glass: `slice[int]` is generic now. Souvenir.")
    r.say('solve A', "A: the closed ledger. TypedDict, PEP 728.")
    r.attempt('typeddict',
              "Two class arguments: `closed=True` shuts out typos like `yaer`, and `extra_items=float` lets "
              "the Vigil accept any number of float readings.", source=S['typeddict'], expect=True)
    r.say('solve B', "B: TypeForm, PEP 747.")
    r.attempt('typeform',
              "I know how to say \"a class\": `type[T]`. Surely that's close enough?",
              source="from typing import Any\n\n\ndef parse[T](kind: type[T], raw: str) -> T:\n"
                     "    if kind is int:\n        return int(raw)\n    if kind is float:\n"
                     "        return float(raw)\n    return raw\n", expect=False)
    r.note("Not close enough. `type[T]` means *a class object*. `str | None` and `list[int]` are type "
           "**expressions** but not classes. `TypeForm[T]` is the word for *\"the thing you write to mean T\"*.")
    r.attempt('typeform', "`TypeForm[T]` from `typing`, with a PEP 695 type parameter.", source=S['typeform'], expect=True)
    r.say('solve C', "C: disjoint bases, PEP 800.")
    r.attempt('disjoint-base',
              "\"Two classes that can't be combined.\" Intuitively I want to mark the *combination* as bad, so I'll "
              "decorate `Both`...",
              source="from typing import disjoint_base\n\n\nclass Reader:\n    \"\"\"Holds a buffer it only ever reads from.\"\"\"\n\n\n"
                     "class Writer:\n    \"\"\"Holds a buffer it only ever writes to.\"\"\"\n\n\n"
                     "@disjoint_base\nclass Both(Reader, Writer):\n    \"\"\"Neither one thing nor the other.\"\"\"\n",
              expect=False)
    r.note("Backwards. The rule is about the *pair of bases*. Each one declares itself a disjoint base, and "
           "then a checker refuses any class that inherits from both. This is how typeshed can describe "
           "what CPython itself forbids, like `class X(int, str)`.")
    r.attempt('disjoint-base', "Decorating both bases and leaving `Both` alone, so pyrefly gets to reject it.",
              source=S['disjoint-base'], expect=True)

    # --------------------------------------------------------------- Crypt
    r.chap('crypt', 'The Deprecation Crypt', 'What 3.15 removed')
    r.say('north', "North into the Crypt. *\"Every stone down here was a DeprecationWarning that somebody scrolled past.\"* Ouch.")
    r.say('examine ledger', "The ledger lists what's deprecated *now*, for removal later. Worth a read.")
    r.say('solve', "")
    r.attempt('removals',
              "Four graves. `sre_parse` → `re.compile`. `glob.glob1` → `glob.glob(..., root_dir=root)`. "
              "`co_lnotab` → `co_lines()`. The fourth is `strptime('%m-%d')`... that looks fine to me? Let me fix "
              "three and see.",
              source='import glob\nimport re\nfrom datetime import datetime\n\n\ndef compiled(pattern):\n'
                     '    return re.compile(pattern)\n\n\ndef python_files(root):\n'
                     "    return sorted(glob.glob('*.py', root_dir=root))\n\n\ndef release_day(text):\n"
                     "    # The caller now passes dates like '2026-03-20'.\n"
                     "    return datetime.strptime(text, '%m-%d')\n\n\ndef line_numbers(function):\n"
                     '    return list(function.__code__.co_lines())\n',
              expect=False)
    r.note("So `%d` without a year is now an **error**, not just a warning, because it silently defaulted to 1900 "
           "(and February 29 broke). The caller passes full ISO dates anyway, so `%Y-%m-%d` is the fix.")
    r.attempt('removals', "All four fixed.", source=S['removals'], expect=True)

    # ---------------------------------------------------------------- Loop
    r.chap('loop', 'The Great Loop', 'The colorful hub, and the barred gate')
    r.say('east', "East, into the center of the building.")
    r.say('examine gate', "The gate north is barred. How many sigils does it want?")
    r.say('take swatch', "A swatch of colors: argparse, difflib, ast, sqlite3 and friends all print in color now.")
    r.say('map', "Let me look at the map. The Gate is directly north of here.")

    # -------------------------------------------------------------- Oracle
    r.chap('oracle', 'The Error Oracle', 'Improved error messages · re.prefixmatch')
    r.say('down', "Down the spiral staircase into *\"somewhere much older\"*.")
    r.say('solve A', "A: four tracebacks from people writing another language's method names. The starter literally says *Press Check* to hear the Oracle. So I will.")
    r.attempt('oracle', "Submitting the broken code as-is, just to see what 3.15 says back.", source=None, expect=False)
    r.note("This is lovely. 3.15 recognizes **JavaScript/Java/Ruby/C#** method names: `push` → *Did you mean "
           "'.append'?*, `toUpperCase` → `.upper`, `put` → *Use d[k] = v*, and appending to a tuple → *Did you mean "
           "to use a 'list' object?* The fixes are now obvious.")
    r.attempt('oracle', "Taking the Oracle's advice, line by line.", source=S['oracle'], expect=True)
    r.say('solve B', "B: *\"The most expensive name in the standard library.\"* `re.match`!")
    r.attempt('prefixmatch',
              "`re.match` only matches at the start, which surprises everyone coming from other languages. 3.15 adds "
              "`re.prefixmatch` as the explicit name. The *second* function was the real bug: it wants `re.search`.",
              source=S['prefixmatch'], expect=True)
    r.say('up', "Back up to the Loop.")

    # ------------------------------------------------------------- Gardens
    r.chap('gardens', 'The Comprehension Gardens', 'PEP 798 · * and ** in comprehensions')
    r.say('south', "South to the Gardens.")
    r.say('examine shed', "")
    r.say('solve', "")
    r.attempt('unpacking',
              "Let me try the way I've written it for a decade, with `itertools.chain.from_iterable`...",
              source="import itertools\n\nbeds = [['fern', 'moss'], ['ivy'], ['thyme', 'sage', 'rue']]\n"
                     "labels = [{'fern': 'shade'}, {'ivy': 'climber'}, {'fern': 'damp shade'}]\n\n"
                     "plants = list(itertools.chain.from_iterable(beds))\n"
                     "legend = {k: v for label in labels for k, v in label.items()}\n",
              expect=False)
    r.note("*\"itertools.chain is the old way round this.\"* The checker reads **how** I wrote it, not just the "
           "values. PEP 798 extends PEP 448's `*`/`**` from displays into comprehensions.")
    r.attempt('unpacking', "`[*bed for bed in beds]` and `{**label for label in labels}`. This is valid syntax now.",
              source=S['unpacking'], expect=True)
    r.note("**The asterisk key**, another sigil. This one feels like it should always have been allowed.")
