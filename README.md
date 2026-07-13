# codegen — a code that codes

A zero-dependency Python code generator. Tell it what you want; it prints
ready-to-run Python source to stdout (or a file with `-o`). Every generator
compiles its output before emitting it, so it refuses to hand you broken code.

## Usage

```sh
# a dataclass with typed fields
python3 codegen.py class Point --fields x:float y:float

# an argparse CLI scaffold
python3 codegen.py cli greet --args name --flags loud

# a tiny stdlib HTTP JSON API
python3 codegen.py api todo --routes list get create

# and, of course: code that codes itself
python3 codegen.py quine
```

Write to a file instead of stdout with `-o`:

```sh
python3 codegen.py api todo --routes list -o server.py
python3 server.py   # serves on http://127.0.0.1:8000
```

## The quine

`codegen.py quine` emits a program whose output is byte-for-byte its own
source — the purest possible answer to "code me a code that codes":

```sh
python3 codegen.py quine -o q.py
python3 q.py | diff - q.py   # no difference
```

Requires Python 3.8+. No dependencies.

## Bonus: BOSS FIGHT — Jerry, the Possessed Snowman

A zero-dependency terminal boss battle. Full backstory in [LORE.md](LORE.md);
the short version:

1. Jerry got possessed by the Hollow Soul.
2. We kill the soul (aim for the dark shard — NOT Jerry).
3. Jerry happy.
4. Jerry is ⬆️.

```sh
python3 boss_jerry.py            # interactive fight
python3 boss_jerry.py --auto     # watches itself win, no input needed
python3 boss_jerry.py --seed 7   # deterministic RNG
```
