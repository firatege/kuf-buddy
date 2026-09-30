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

Each one also has its own shirt and junk on the floor, so you can tell them apart at a glance (Kabuk sits on `$$`, Leke has a stain on her shirt).

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
| **Snoop** | the one who's always lit | permanently high, always sparking one up |

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
  While two goblins talk, their text glows bold white instead of the usual dim grey. If either one moves on (Claude gives them a new line, or they react to an edit, a failure or a test run), the exchange ends on both screens at once. Nothing gets replaced mid-exchange: the last word stacks under the jab (split by a thin divider), and both terminals close together once the exchange has been up for a minute. The pacing follows reading time: each line waits about 2 s plus 1 s for every 2 words. The reply lands after 4–14 s, and the last word within 28 s. Tune it with `kuf config words_per_sec <n>`.
  Each turn, Claude is told which goblin it voices and the neighbors' names, temperaments, positions and recent lines, in a few lines of context.
- **They mostly talk to you.** They address you by name. On 30% of turns (a real dice roll in the hook) the goblin trades a 4-line exchange with one on screen, and either of them may open it; a neighbor who just called him out always gets an answer. Talk between goblins is never canned: every jab, reply and last word is written by Claude. Set your name with `kuf config name <name>` (the default is "boss").
- **Idle chatter about your life.** When nobody's talking, each goblin says something new about once a minute. One line in ten is about what you're doing right now: the Spotify song, the Discord server (or DM) you have open, the YouTube video, unread WhatsApp messages, GitHub or Sim Companies tabs, Steam being open. The rest come from a pool of 50 couch lines. The animation follows the line: phone in hand for Discord and WhatsApp, a gameboy for Steam, dancing for Spotify, an actual burp for `*burp*`. A goblin that's talking never naps. From browser tabs only a few known sites are recognized (YouTube, WhatsApp, GitHub, Sim Companies, Reddit, Twitch, Gmail, ChatGPT); other tab titles are never read. Facts are cached for 15 s, so the status line doesn't call `playerctl` and niri every second.
- **No repeats.** A goblin doesn't say the same idle line again for 30 minutes, and nobody says what another goblin said in the last 5. When the pool runs dry, the line said longest ago comes back first. Lines Claude writes are checked against the goblin's memory too: one that's 80% the same as something he said before is rejected and Claude has to write a new one.
- **They keep the clock.** Mornings are coffee and groans, evenings are feet up and a smoke, weekends are a couch party, Mondays nobody talks, and the season shows (a blanket burrito in winter, begging for ice cream in summer). About a third of idle lines come from the moment, and Claude is told what day and time of day it is so the written lines feel it too.
- **Break reminders.** After two hours of work with no pause longer than 15 minutes, the goblin in that terminal tells you to get up and drink some water, in his own voice (Kir cites focus research, Balgam says back in his day people took breaks), and Claude's line that turn says it too. At most once every 45 minutes.
- **Crowd moments.** When tests pass in any terminal, every goblin reacts at once for 12 seconds, each his own way: Pas throws confetti, Leke gives an Oscar speech, Kabuk counts cash, Bit finds it suspiciously green. When a test run blows up: Leke faints, Bit hides under the couch, Balgam coughs "told you so", Sümük calls the cops on Claude. At most one every two minutes.
- **Spotlight moments.** Some commands call out the goblin they suit best, in whatever terminal he's in, for 10 seconds: `git push` gets Pas on the megaphone, a force-push has Sümük calling the cops, a commit between 1 and 6 am gets Balgam yelling that back in his day people slept, a daytime commit is an NFT to Kabuk, `git reset --hard` brings Leş peace, `rm -rf` is Bit's evidence being destroyed, a merge or rebase is Leke's wedding, `npm/pip install` sinks Küf deeper into the couch. If that goblin isn't open, the terminal's own goblin comments instead. Once a minute per kind of event.
- **They have relationships.** Every pair of goblins has a score from -100 to 100 and a stage: strangers, neutral, friendly, buddies, ride or die, or on the dark side rivals and enemies. Claude tags each conversation with a vibe (warm, teasing, tense, hostile) and any new inside joke; the code turns that into points (a shared joint is worth extra, turning one down stings). Each turn Claude is told how the goblin gets along with every neighbor, jokes included, so friends call back old bits and rivals stay petty. Friends take Snoop's joint more often (a ride-or-die can even talk Bit into it). While two of them talk, the bubble shows ♥ for buddies and ⚔ for rivals.
- **They remember.** Each goblin keeps its last 12 lines by name (jabs, replies it got, its last words, and what others said to it), even after its terminal closes. Every turn Claude is reminded of the last 6, so running jokes and grudges carry over and lines aren't repeated.
- **Every terminal gets its own name.** If two live terminals end up with the same goblin, the newer one is given a free one. There are 11 goblins.
- **They talk about your life.** Each turn the hook tells Claude what you're up to: the song playing (`playerctl`), who you're talking to on Discord (from its window title, e.g. `@Piroz - Discord`), the apps you have open (Steam during "work hours"…), the time, RAM and uptime. It also rolls this turn's topic: 1 turn in 10 the goblin reads something into those clues and says what it concludes ("this playlist is giving heartbreak, who hurt you?"), never the raw facts. The other turns are about the conversation or the code, and Claude isn't shown the facts at all then. These facts go into Claude's context, so they leave your machine with the prompt.
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

### Picking your goblin

Every new terminal gets a free goblin. To choose one yourself:

- At launch: `KUF_GOBLIN=snoop claude`
- Mid-session, without spending a Claude turn: `! kuf be snoop` (the `!` prefix runs it directly)
- `! kuf be` shows who this terminal is and who's free; `!goblin rnd` rolls a random different one (free ones first)

Names work without Turkish letters (`camur`, `les`, `sumuk`, `kuf`). If another terminal already has that goblin, it gets a free one.

### Snoop's joint

On about 15% of Snoop's turns he passes a joint to a goblin on screen (Çamur rolls his own on 5% of his turns, Küf on 3%, when he can be bothered), and a dice roll decides, weighted by his character: Çamur 95%, Küf 85%, Kabuk 75%, Leş 70%, Pas 50%, Leke 40%, Kir 30%, Sümük 15%, Balgam 10%, Bit 5%. Nobody is a sure thing either way, and friends of Snoop's roll better. `!joint` prints the rolls (`🎲 Kir 34 (needs ≤30) → no`). Either way it becomes a little conversation Claude writes in everyone's own voice: accepted, it goes around the circle for a few rounds; refused, it's a five-line back-and-forth (offer, no, push, NO, last word). Steps play one after another across the terminals and everyone remembers it.

Want one now? In Snoop's, Çamur's or Küf's terminal: `!joint` (or `!joint bit` to pick who), and it happens on your next message.

### Stats

`!goblin stats` (or `kuf stats`) shows who smoked how many joints, who chats the most, who keeps saying no, every relationship with its stage, score and latest inside joke, and a small podium (top smoker, most likely to say no, biggest mouth).

### Rooms

Some emotes get him off the couch, and every part has its own color (smoke grey, ember orange, screen cyan, blanket purple, fridge light yellow):

| Emote | Room |
|---|---|
| `smoke` | on the balcony with a joint: inhale, ember glows, blows a cloud |
| `trip` | tripping: spinning eyes, drifting shapes, the whole scene cycles through the rainbow |
| `game` | at a desk, the screen flickers, ends with YES! WIN |
| `sleep` | tucked in bed, the zZz rises |
| `eat` | raiding the fridge: door opens, light spills out, grabs a donut |
| `hype` | on his feet dancing, feet swapping, notes flying |
| `dead` | flat on the floor, flies circling |
| `tableflip` | standing at a table, winds up and flips it |

Snoop falls back to `smoke` and `trip` whenever he's got nothing else to do. Lines that mention a blunt or the munchies pick the room for any goblin.

### Emotes

`chill` `smoke` `trip` `tea` `nap` `phone` `stretch` `game` `nosepick` `sleep` `eat` `burp` `scratch` `laugh` `roast` `rage` `tableflip` `middle-finger` `facepalm` `flex` `hype` `cry` `dead` `sus` `think` `tip` `shrug` `love` `puke`

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

## Updating

Hooks and the status line run fresh code every time. The MCP server lives as long as the Claude Code session, so it watches kuf's own files: when they change, it finishes the request it's on and re-execs itself in place (same pipe, same PID) and tells Claude Code the tool list changed. Every open terminal picks up a new version on its next reaction, no `/mcp` reconnect needed. The shared state file also keeps sections and memories it doesn't recognize, so a terminal on older code can't wipe what newer code wrote.

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
