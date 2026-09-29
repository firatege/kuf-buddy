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
| **Hooks** | Watch file edits, prompt edits (`CLAUDE.md`, rules, skills…), failed commands and passing tests. If Claude forgets to react, a Stop hook picks a canned solo line so he's never silent. Idle, night and greeting lines are canned too. |
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
| **Çamur** | mud | spaced-out stoner philosopher |
| **Balgam** | phlegm | cranky old boomer, hates new tech |
| **Bit** | louse | paranoid conspiracy nut |
| **Leke** | stain | dramatic diva, everything is a tragedy |
| **Kabuk** | scab | sleazy hustler, sells you crypto |

Split your screen and they trash-talk each other:

```
  ·lmao       ╭─ Sümük ──────────────────────────────────────────────────╮
 (☞ﾟヮﾟ)☞     < Küf on the right (ced-demo) talking shit again. i'll eat │
/|▓▓▓|\ ,,    │ your crumbs, bitch.                                      │
▀█▀▀▀▀▀▀█▀    ╰──────────────────────────────────────────────────────────╯
```

- **Written exchanges.** When Claude jabs a neighbor (`kuf_react(to=...)`), it also writes the neighbor's `reply` in *their* temperament, plus its own `last_word`. Both are required: a jab without them is rejected, and Claude has to try again. The exchange then plays out across the two terminals:
  ```
  left,  0s:   yo Pas, your tests are fake
  right, 5s:   fake? at least i HAVE tests           ← Pas answers in his own terminal
  left,  11s:  one test. it asserts True.            ← last word
  ```
  Nothing gets replaced mid-exchange: the last word stacks under the jab (split by a thin divider), and both terminals close together once the exchange has been up for a minute. The pacing follows reading time: each line waits about 2 s plus 1 s for every 2 words. The reply lands after 4–14 s, and the last word within 28 s. Tune it with `kuf config words_per_sec <n>`.
  Each turn, Claude is told which goblin it voices and the neighbors' names, temperaments, positions and recent lines, in a few lines of context.
- **They mostly talk to you.** They address you by name and only clap back at each other when someone calls them out, or roughly one time in four. Talk between goblins is never canned: every jab, reply and last word is written by Claude. Set your name with `kuf config name <name>` (the default is "boss").
- **Idle chatter about your life.** When nobody's talking, each goblin says something new about every 20 seconds. Three lines in four are about what you're doing right now: the Spotify song, the Discord server (or DM) you have open, the YouTube video, unread WhatsApp messages, GitHub or Sim Companies tabs, Steam being open. The rest come from a pool of 50 couch lines. From browser tabs only a few known sites are recognized (YouTube, WhatsApp, GitHub, Sim Companies, Reddit, Twitch, Gmail, ChatGPT); other tab titles are never read. Facts are cached for 15 s, so the status line doesn't call `playerctl` and niri every second.
- **They remember.** Each goblin keeps its last 12 lines by name (jabs, replies it got, its last words, and what others said to it), even after its terminal closes. Every turn Claude is reminded of the last 6, so running jokes and grudges carry over and lines aren't repeated.
- **Every terminal gets its own name.** If two live terminals end up with the same goblin, the newer one is given a free one. There are 10 goblins.
- **They talk about your life.** Each turn the hook tells Claude what you're up to: the song playing (`playerctl`), who you're talking to on Discord (from its window title, e.g. `@Piroz - Discord`), the apps you have open (Steam during "work hours"…), the time, RAM and uptime. It also rolls this turn's topic: 3 turns out of 4 the goblin talks about that, and the rest of the time about the conversation or the code. These facts go into Claude's context, so they leave your machine with the prompt.
- **They stick to what you can see.** On niri, Claude is told which neighbors are on screen and which are scrolled out of view. niri doesn't report the scroll position, so "on screen" is estimated: start from the focused column and add neighboring columns while they still fit in the monitor's width.
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

When he talks to a neighbor (written replies and last words), he turns to face that terminal. A goblin whose neighbor is on the left is mirrored, and his bubble moves to his mouth side.

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

Küf swears a lot, talks like your street bro and trash-talks your *code* (and Claude). He's loyal to you. He's crude, but he never uses slurs or bigoted jokes. To make him your own, edit `kuf/events.py` (canned solo lines) or the `PERSONA` text in `kuf/mcp_server.py`.

## Uninstall

1. Run `python3 .../bin/kuf uninstall-statusline`.
2. Run `/plugin uninstall kuf-buddy`.
3. Delete `~/.claude/kuf/`, where his state lives.

## Dev

```sh
python3 -m pytest -q
```

MIT © Fırat Ege Bayram
