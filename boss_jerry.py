#!/usr/bin/env python3
"""BOSS FIGHT: Jerry, the Possessed Snowman.

A zero-dependency terminal boss battle. Full backstory in LORE.md.

The lore, short version:
    Jerry got possessed by the Hollow Soul.
    We kill the soul (NOT Jerry -- aim for the dark shard on his chest).
    Jerry happy. The end.

Play it:
    python3 boss_jerry.py            # interactive fight
    python3 boss_jerry.py --auto     # watches itself win (no input needed)
    python3 boss_jerry.py --seed 7   # deterministic RNG
"""

from __future__ import annotations

import argparse
import random
import sys
import time

# --------------------------------------------------------------------------
# art
# --------------------------------------------------------------------------

POSSESSED_JERRY = r"""
                  _______
                 |_______|
                _|_______|_
          \    /  \_/ \_/  \    /
      ~\~~~\~ |    _____    | ~/~~~/~
     ~~\~~~~\~ \  \VVVVV/  / ~/~~~~/~~
       ~\~~~~\~ \  `---'  / ~/~~~~/~
         `~~~~\ (  {: :}  ) /~~~~'
               \ '.__A__.' /
                |* {SOUL} *|      <- the dark shard: STRIKE THE SOUL
                |  * ; *  ;|
               /   *   *   \
              (_____________)
        JERRY, THE POSSESSED SNOWMAN
"""

HOLLOW_SOUL = r"""
              .  *  .   *
           *   .-~~~~~-.  .
             .'  x   x  '.
          * (     ___     ) *
             '.  \___/  .'
           .   '-.....-'   *
              THE HOLLOW SOUL
        (no body left to hide in)
"""

FREE_JERRY = r"""
                 ___
                |___|
               _|___|_
              /  o o  \
             |    >    |
              \  \_/  /       <- that's his real smile
            ~( snowflake )~
             (    o    )
            (     o     )
           (_____________)
             JERRY (HAPPY)
"""



# --------------------------------------------------------------------------
# presentation helpers
# --------------------------------------------------------------------------

FAST = False


def say(text: str = "", pause: float = 0.02) -> None:
    print(text)
    if not FAST:
        time.sleep(pause * min(len(text), 40))


def banner(text: str) -> None:
    say("")
    say("=" * 58)
    say(f"  {text}")
    say("=" * 58)


def bar(label: str, hp: int, hp_max: int, width: int = 24) -> str:
    hp = max(hp, 0)
    filled = 0 if hp == 0 else max(1, round(width * hp / hp_max))
    return f"{label:>12} [{'#' * filled}{'.' * (width - filled)}] {hp}/{hp_max}"


# --------------------------------------------------------------------------
# the fight
# --------------------------------------------------------------------------

class Fighter:
    def __init__(self, name: str, hp: int) -> None:
        self.name = name
        self.hp_max = hp
        self.hp = hp

    def hit(self, dmg: int) -> int:
        self.hp = max(self.hp - dmg, 0)
        return dmg

    @property
    def alive(self) -> bool:
        return self.hp > 0


BOSS_ATTACKS = [
    ("Root Lash", 12, "gnarled root-tentacles whip across the ice!"),
    ("Blizzard Breath", 8, "a howling cone of razor snow!"),
    ("Icicle Grin", 14, "he SMILES at you. The icicles launch."),
]

SOUL_ATTACKS = [
    ("Wail of the Deep", 11, "a thousand-year scream rattles your bones!"),
    ("Grasping Dark", 15, "cold root-shadows claw at your heels!"),
]


def choose(prompt: str, options: list[str], auto_pick: int,
           auto: bool) -> int:
    for i, opt in enumerate(options, 1):
        say(f"   {i}) {opt}", pause=0)
    if auto:
        # auto mode plays like someone who read the lore.
        say(f"{prompt} {auto_pick + 1}", pause=0)
        return auto_pick
    while True:
        raw = input(f"{prompt} ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        say(f"   (pick a number 1-{len(options)})", pause=0)


def boss_turn(rng: random.Random, hero: Fighter, attacks, guarding: bool,
              attacker: str) -> None:
    name, dmg, flavor = rng.choice(attacks)
    dealt = max(dmg // 4, 2) if guarding else dmg
    hero.hit(dealt)
    say(f"\n{attacker} uses {name.upper()}! {flavor}")
    if guarding:
        say(f"You brace behind your shield -- only {dealt} damage.")
    else:
        say(f"You take {dealt} damage!")


def phase_one(rng: random.Random, hero: Fighter, auto: bool) -> bool:
    """Fight the possession. Returns True if the shard breaks (good path)."""
    shard = Fighter("Soul Shard", 300)
    body = Fighter("Jerry's body", 200)
    shields = {"LEFT": 7, "RIGHT": 7}

    banner("PHASE 1 -- JERRY THE SNOWMAN: FROZEN & FORGOTTEN")
    say(POSSESSED_JERRY, pause=0)
    say('"jerry isn\'t home right now," the snowman grins.')
    say("A dark coal shard pulses on his chest where his")
    say("heart-button used to be. That's the anchor. That's the target.")
    say("But both arms are armored in black ice -- a shield on each")
    say("limb, 7 hits apiece, before the shard takes any damage.")

    while shard.alive and hero.alive and body.alive:
        say("")
        say(bar("You", hero.hp, hero.hp_max), pause=0)
        say(bar("Soul Shard", shard.hp, shard.hp_max), pause=0)
        say(bar("Jerry", body.hp, body.hp_max), pause=0)
        for side, hits in shields.items():
            state = "DESTROYED" if hits == 0 else f"{hits} hits left"
            say(f"{side + ' ARM SHIELD':>16}  [{state}]", pause=0)
        say("")

        shields_up = any(shields.values())
        options, keys = [], []
        for side, hits in shields.items():
            if hits > 0:
                options.append(f"Smash the {side} arm shield ({hits} hits left)")
                keys.append("smash" + side)
        if shields_up:
            options.append("Strike the SOUL SHARD (blocked by the shields!)")
        else:
            options.append("Strike the SOUL SHARD (the right target)")
        keys.append("shard")
        if not shields_up:
            options.append("Attack Jerry's body (please don't)")
            keys.append("body")
        options.append("Guard")
        keys.append("guard")

        if hero.hp <= 40:
            auto_pick = keys.index("guard")
        elif shields_up:
            auto_pick = 0
        else:
            auto_pick = keys.index("shard")
        pick = keys[choose("> your move:", options, auto_pick, auto=auto)]

        guarding = False
        if pick.startswith("smash"):
            side = pick[len("smash"):]
            hits = min(rng.randint(1, 3), shields[side])
            shields[side] -= hits
            say(f"\nYou batter the {side} arm shield -- {hits} hit(s)!")
            if shields[side] == 0:
                say(f"*** {side} ARM SHIELD DESTROYED ***")
                if not any(shields.values()):
                    say("Both shields are down. The dark shard is exposed!")
        elif pick == "shard":
            if shields_up:
                say("\nYour blade glances off the black ice. BLOCKED.")
                say("(Smash both arm shields first -- 7 hits each.)")
            else:
                dmg = rng.randint(30, 55)
                shard.hit(dmg)
                say(f"\nYou drive your blade at the dark shard -- {dmg} damage!")
                say("The Hollow Soul SHRIEKS through Jerry's stolen mouth.")
        elif pick == "body":
            dmg = rng.randint(40, 70)
            body.hit(dmg)
            say(f"\nYou knock snow off Jerry -- {dmg} damage... to JERRY.")
            say("The Hollow Soul laughs. Jerry's little scarf droops.")
            say("(Strike the soul, not the snowman!)")
        else:
            guarding = True
            heal = rng.randint(12, 20)
            hero.hp = min(hero.hp + heal, hero.hp_max)
            say(f"\nYou raise your guard and catch your breath (+{heal} HP).")

        if not shard.alive:
            break
        boss_turn(rng, hero, BOSS_ATTACKS, guarding, "Jerry the Snowman")

    if not body.alive:
        say("\nJerry's body collapses into a sad, quiet pile of snow.")
        say("The Hollow Soul slips away laughing, to find another host.")
        banner("BAD END -- YOU KILLED JERRY, NOT THE SOUL. READ THE LORE.")
        return False
    if not hero.alive:
        return False

    say("\nCRACK. The dark shard splits down the middle!")
    say("The Hollow Soul is RIPPED out of Jerry's body --")
    say("Jerry shrinks, tentacles crumbling to dust around him.")
    return True


def phase_two(rng: random.Random, hero: Fighter, auto: bool) -> bool:
    """We kill the soul. Returns True if the Hollow Soul is destroyed."""
    soul = Fighter("Hollow Soul", 150)

    banner("PHASE 2 -- WE KILL THE SOUL")
    say(HOLLOW_SOUL, pause=0)
    say("A shrieking knot of black roots and cold light.")
    say("No body to hide in. No mercy left to ask for.")

    while soul.alive and hero.alive:
        say("")
        say(bar("You", hero.hp, hero.hp_max), pause=0)
        say(bar("Hollow Soul", soul.hp, soul.hp_max), pause=0)
        say("")

        pick = choose("> your move:", [
            "Attack the Hollow Soul",
            "Guard",
        ], auto_pick=1 if hero.hp <= 40 else 0, auto=auto)

        guarding = False
        if pick == 0:
            dmg = rng.randint(30, 55)
            soul.hit(dmg)
            say(f"\nYou cut through the cold light -- {dmg} damage!")
        else:
            guarding = True
            heal = rng.randint(12, 20)
            hero.hp = min(hero.hp + heal, hero.hp_max)
            say(f"\nYou raise your guard and catch your breath (+{heal} HP).")

        if not soul.alive:
            break
        boss_turn(rng, hero, SOUL_ATTACKS, guarding, "The Hollow Soul")

    if not hero.alive:
        return False

    say("\nThe Hollow Soul unravels, root by root, into nothing.")
    say("After a thousand years under Frostfall Hill... it is over.")
    return True


def ending() -> None:
    banner("JERRY HAPPY")
    say(FREE_JERRY, pause=0)
    say("Three snowballs tall. Crooked carrot nose. Top hat: intact.")
    say('"...you came back for me," Jerry says, and smiles')
    say("at absolutely everyone.")

    say("")
    say("        J E R R Y   H A P P Y")
    say("")


def main(argv: list[str] | None = None) -> int:
    global FAST
    parser = argparse.ArgumentParser(
        prog="boss_jerry",
        description="Boss fight: free Jerry from the Hollow Soul (see LORE.md).",
    )
    parser.add_argument("--auto", action="store_true",
                        help="the fight plays itself (also implies --fast)")
    parser.add_argument("--fast", action="store_true", help="no dramatic pauses")
    parser.add_argument("--seed", type=int, default=None,
                        help="seed the RNG for a deterministic fight")
    opts = parser.parse_args(argv)

    FAST = opts.fast or opts.auto
    rng = random.Random(opts.seed)
    hero = Fighter("You", 120)

    banner("FROSTFALL HILL -- MIDWINTER, AT NIGHT")
    say("Jerry was the happiest snowman on Frostfall Hill.")
    say("Then something old crawled up out of the frozen ground.")
    say("Tonight, you end this.")

    if not phase_one(rng, hero, opts.auto):
        if not hero.alive:
            banner("YOU FELL. FROSTFALL HILL STAYS COLD. TRY AGAIN.")
        return 1

    heal = min(60, hero.hp_max - hero.hp)
    hero.hp += heal
    say(f"\nWith the shard broken, warmth returns to the hill (+{heal} HP).")

    if not phase_two(rng, hero, opts.auto):
        banner("SO CLOSE. THE SOUL SLIPS BACK INTO THE EARTH. TRY AGAIN.")
        return 1

    ending()
    return 0


if __name__ == "__main__":
    sys.exit(main())
