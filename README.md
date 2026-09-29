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

### Emotes

`chill` `sleep` `eat` `burp` `scratch` `laugh` `roast` `rage` `tableflip` `middle-finger` `facepalm` `flex` `hype` `cry` `dead` `sus` `think` `tip` `shrug` `love` `puke`

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
