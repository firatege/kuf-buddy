# Küf

**A filthy, ugly, extremely comfortable ASCII couch goblin who lives in your Claude Code status line.**

He naps on a stained couch until something happens. Then he roasts your code, loses his mind when anyone touches your prompts, grudgingly praises your wins and sometimes drops a trick that actually helps.

```
 °#·#°        ╭─ Küf ────────────────────────────────────────────────────╮
 (╬ಠ益ಠ)      < claude rewrote a prompt (CLAUDE.md). who the fuck asked? │
/|▓▓▓|\ ##    ╰──────────────────────────────────────────────────────────╯
▀█▀▀▀▀▀▀█▀

 °  !         ╭─ Küf ────────────────────────────────────────────────────╮
 (•̀ᴗ•́)☝       < pro tip: bisect finds the change that broke your shit in │
/|▓▓▓|\ ,,    │ log2(n) steps                                            │
▀█▀▀▀▀▀▀█▀    ╰──────────────────────────────────────────────────────────╯

  ✦ ·         ╭─ Küf ─────────────────────────────────────────────────╮
ᕦ(ò‿óˇ)ᕤ      < tests green?? who are you and what did you do with my │
 |▓▓▓| ,,     │ boy.                                                  │
▀█▀▀▀▀▀▀█▀    ╰───────────────────────────────────────────────────────╯
```

*Küf* is Turkish for "mold". It fits.

## How he works

| Piece | What it does |
|---|---|
| **MCP server** (`kuf`) | Gives Claude a `kuf_react(emote, line)` tool plus Küf's persona. Near the end of each turn, Claude voices Küf with a line about what actually happened. Claude's own replies stay normal. |
| **Hooks** | Watch file edits, prompt edits (`CLAUDE.md`, rules, skills…), failed commands and passing tests. If Claude forgets to react, a Stop hook picks a canned line so he's never silent. |
| **Status line** | Draws Küf with 2-frame animation (it refreshes every second) and a speech bubble. His mood (comfy, sleepy, grumpy, furious) drifts with what's been going on. |

It needs only standard-library Python 3.10+. No dependencies, no API keys.

### The couch gang: one goblin per terminal

Every open Claude Code terminal gets its own goblin, each with its own mood, memory and temperament. No two live terminals share one.

| Goblin | Means | Temperament |
|---|---|---|
| **Küf** | mold | lazy, grumpy slob |
| **Pas** | rust | hyperactive hype-man, ALL CAPS |
| **Leş** | carcass | dead-inside nihilist |
| **Sümük** | snot | petty snitch, keeps score |
| **Kir** | grime | smug know-it-all, drops tricks |

Split your screen and they trash-talk each other:

```
  ·lmao       ╭─ Sümük ──────────────────────────────────────────────────╮
 (☞ﾟヮﾟ)☞     < Küf on the right (ced-demo) talking shit again. i'll eat │
/|▓▓▓|\ ,,    │ your crumbs, bitch.                                      │
▀█▀▀▀▀▀▀█▀    ╰──────────────────────────────────────────────────────────╯
```

- **Written exchanges.** When Claude jabs a neighbor (`kuf_react(to=...)`), it also writes the neighbor's `reply` in *their* temperament, plus an optional `last_word`. The exchange then plays out across the two terminals:
  ```
  left,  0s:   yo Pas, your tests are fake
  right, 2s:   fake? at least i HAVE tests           ← Pas answers in his own terminal
  left,  4.5s: one test. it asserts True.            ← last word
  ```
  The pacing follows reading time: each line waits about 1 s plus 1 s for every 4 words. The reply lands after 2–6 s, and the last word within 12 s. Tune it with `kuf config words_per_sec <n>`.
  Each turn, Claude is told which goblin it voices and the neighbors' names, temperaments, positions and recent lines, in a few lines of context.
- **Instant canned retorts.** If nobody wrote a reply, the neighbor answers from a canned pool within a second. The pool is picked by topic (tests, failures, heat, laziness, code, music, smell, snitching, praise), so the answer fits what was said. A goblin called out by name always answers, and harder. Other lines get an answer about one time in three.
- **They mostly talk to you.** They address you by name and only clap back at each other when someone calls them out, or roughly one time in three. Set your name with `kuf config name <name>` (the default is "boss").
- **They gossip about you.** Every 4 minutes, two goblins have a short chat in their status lines, one line at a time. They talk about your battery and CPU temperature, the song playing, the apps you have open (Steam during "work hours"…), the time, uptime, RAM, and the files you've been touching:
  ```
   Kir [puke]: laptop's at 94°C. i could fry an egg on this couch
   Leş [roast]: that's not an egg Kir, that's your face melting
   Kir [rage]: boss needs a cooling pad or a priest
  ```
  All of this data is read locally: `/sys`, `/proc`, `playerctl`, and app names from niri (never window titles). Nothing leaves your machine.
- **They stick to what you can see.** On niri, gossip pairs are picked from the terminals that are actually on screen, and canned retorts ignore goblins that are scrolled out of view unless those goblins called them out by name. Claude is told which neighbors are off screen too. niri doesn't report the scroll position, so "on screen" is estimated: start from the focused column and add neighboring columns while they still fit in the monitor's width.
- **They know where they sit.** On [niri](https://github.com/YaLTeR/niri), goblins find each other's windows and say "on the right", "right above you" or "way off to the left". Everywhere else, they use the project name.

### Life on the couch

He actually sits on a couch now, armrests and all. When nobody is talking to him, he looks straight ahead and lives his life in 4-frame loops, one frame per second:

```
    ~                      z
   (-‿-) 旦    tea                    nap        beep          phone
▐▌/|▓▓▓|ﾉ▐▌,,          ▐▌(-.-)▓▓▐▌,,      (°▽°)▣        (・_・)▯
▐█▄▄▄▄▄▄▄█▌            ▐█▄▄▄▄▄▄▄█▌
```

The loops are sipping tea (the steam moves), napping stretched along the couch (the zZ rises), gaming, doomscrolling, yawning and stretching, and picking his nose.

When he talks to a neighbor (written replies, last words, retorts or gossip), he turns to face that terminal. A goblin whose neighbor is on the left is mirrored, and his bubble moves to his mouth side.

### Emotes

`chill` `tea` `nap` `phone` `stretch` `game` `nosepick` `sleep` `eat` `burp` `scratch` `laugh` `roast` `rage` `tableflip` `middle-finger` `facepalm` `flex` `hype` `cry` `dead` `sus` `think` `tip` `shrug` `love` `puke`

See them all:

```sh
./bin/kuf preview --all
```

## Install

```
/plugin marketplace add firatege/kuf-buddy
/plugin install kuf-buddy@kuf-buddy
```

Plugins can't set a status line, so give Küf his couch once:

```sh
python3 ~/.claude/plugins/marketplaces/kuf-buddy/bin/kuf install-statusline
```

This command backs up `~/.claude/settings.json` first, and it tells you if it's replacing another status line. Restart Claude Code afterwards.

## Commands

```sh
kuf preview [emote|--all]                # gallery
kuf say roast "nice null check, genius"  # make him talk right now
kuf install-statusline | uninstall-statusline
```

## Personality

Küf swears a lot, talks like your street bro and trash-talks your *code* (and Claude). He's loyal to you. He's crude, but he never uses slurs or bigoted jokes. To make him your own, edit `kuf/events.py` (canned lines) or the `PERSONA` text in `kuf/mcp_server.py`.

## Uninstall

1. Run `python3 .../bin/kuf uninstall-statusline`.
2. Run `/plugin uninstall kuf-buddy`.
3. Delete `~/.claude/kuf/`, where his state lives.

## Dev

```sh
python3 -m pytest -q
```

MIT © Fırat Ege Bayram
