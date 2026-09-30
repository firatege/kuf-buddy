"""Rooms: emotes that get him off the couch. Each frame is 4 rows plus a same-shaped
mask whose letters pick a color role (see render.ROLE_COLORS): '.' is the goblin himself,
s smoke, e ember, g weed, c screen, y light/glow, w wood, b bed, m metal, r rainbow.
'▓' marks his shirt, swapped for each goblin's own pattern.
"""

ROOMS: dict[str, dict] = {
    "smoke": {
        "desc": 'sparking one up on the balcony, blowing clouds',
        "frames": [
            ['          ~     ', '   (˘‿˘)y═*     ', '    /|▓▓▓|      ', ' ╫══╫══╫══╫══╫  '],
            ['        ░ ~     ', '   (˘ε˘)y═✸     ', '    /|▓▓▓|      ', ' ╫══╫══╫══╫══╫  '],
            ['  ░▒▓▒░  ~      ', '   (ˆoˆ)y═*     ', '    /|▓▓▓|      ', ' ╫══╫══╫══╫══╫  '],
            [' ░  ▒ ░   ·     ', '   (-‿-)y═·     ', '    /|▓▓▓| ahh  ', ' ╫══╫══╫══╫══╫  '],
        ],
        "masks": [
            ['          s     ', '   ...... e     ', '    ......      ', ' wwwwwwwwwwwww  '],
            ['        s s     ', '   ...... e     ', '    ......      ', ' wwwwwwwwwwwww  '],
            ['  sssss  s      ', '   ...... e     ', '    ......      ', ' wwwwwwwwwwwww  '],
            [' s  s s   s     ', '   ...... e     ', '    ......      ', ' wwwwwwwwwwwww  '],
        ],
    },
    "trip": {
        "desc": 'tripping balls, the colors are breathing',
        "frames": [
            [' ✧   ◇   ○   ✦  ', '    (@‿@)  ~    ', '   ~|▓▓▓|~      ', '  ▐█▄▄▄▄▄█▌     '],
            ['   ✦   ✧   ◇  ○ ', '  ~ (◎‿◎)       ', '   ≈|▓▓▓|≈      ', '  ▐█▄▄▄▄▄█▌     '],
            [' ○  ✦   ✧   ◇   ', '    (⊙▽⊙)  ~    ', '   ~|▓▓▓|~ woah ', '  ▐█▄▄▄▄▄█▌     '],
            ['  ◇  ○   ✦   ✧  ', '  ~ (@▽@)  ~    ', '   ≈|▓▓▓|≈      ', '  ▐█▄▄▄▄▄█▌     '],
        ],
        "masks": [
            [' rrrrrrrrrrrrr  ', '    ..... r     ', '   r.....r      ', '  rrrrrrrrr     '],
            ['   rrrrrrrrrrrr ', '  r .....       ', '   r.....r      ', '  rrrrrrrrr     '],
            [' rrrrrrrrrrrr   ', '    ..... r     ', '   r.....r      ', '  rrrrrrrrr     '],
            ['  rrrrrrrrrrrr  ', '  r ..... r     ', '   r.....r      ', '  rrrrrrrrr     '],
        ],
    },
    "game": {
        "desc": 'hunched over a glowing screen, button mashing',
        "frames": [
            ['  ┌─────┐  beep ', '  │▚▞▚▞▚│ (ò_ó) ', '  └──┬──┘/|▓▓▓|ﾉ', '  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔'],
            ['  ┌─────┐  boop ', '  │▞▚▞▚▞│ (°o°) ', '  └──┬──┘/|▓▓▓|ﾉ', '  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔'],
            ['  ┌─────┐  beep ', '  │▚▞▚▞▚│ (ò_ó) ', '  └──┬──┘/|▓▓▓|ﾉ', '  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔'],
            ['  ┌─────┐  YES! ', '  │ WIN │ (≧▽≦) ', '  └──┬──┘\\|▓▓▓|/', '  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔'],
        ],
        "masks": [
            ['  mmmmmmm       ', '  mcccccm ..... ', '  mmmmmmm.......', '  wwwwwwwwwwwwww'],
            ['  mmmmmmm       ', '  mcccccm ..... ', '  mmmmmmm.......', '  wwwwwwwwwwwwww'],
            ['  mmmmmmm       ', '  mcccccm ..... ', '  mmmmmmm.......', '  wwwwwwwwwwwwww'],
            ['  mmmmmmm  yyyy ', '  mcccccm ..... ', '  mmmmmmm.......', '  wwwwwwwwwwwwww'],
        ],
    },
    "sleep": {
        "desc": 'tucked in bed, snoring',
        "frames": [
            ['            z   ', '  ▗▄▄▄▄▄▄▄▄▄▖   ', '  ▐(-_-)░░░░▌   ', '  ▝▀▀▀▀▀▀▀▀▀▘   '],
            ['           zZ   ', '  ▗▄▄▄▄▄▄▄▄▄▖   ', '  ▐(-_-)░░░░▌   ', '  ▝▀▀▀▀▀▀▀▀▀▘   '],
            ['          zZz   ', '  ▗▄▄▄▄▄▄▄▄▄▖   ', '  ▐(-o-)░░░░▌   ', '  ▝▀▀▀▀▀▀▀▀▀▘   '],
            ['        Zzz     ', '  ▗▄▄▄▄▄▄▄▄▄▖   ', '  ▐(-_-)░░░░▌   ', '  ▝▀▀▀▀▀▀▀▀▀▘   '],
        ],
        "masks": [
            ['            s   ', '  bbbbbbbbbbb   ', '  b.....bbbbb   ', '  bbbbbbbbbbb   '],
            ['           ss   ', '  bbbbbbbbbbb   ', '  b.....bbbbb   ', '  bbbbbbbbbbb   '],
            ['          sss   ', '  bbbbbbbbbbb   ', '  b.....bbbbb   ', '  bbbbbbbbbbb   '],
            ['        sss     ', '  bbbbbbbbbbb   ', '  b.....bbbbb   ', '  bbbbbbbbbbb   '],
        ],
    },
    "eat": {
        "desc": 'raiding the fridge, munchies',
        "frames": [
            [' ┌───┐          ', ' │   │  (¬‿¬)   ', ' │  ▪│ /|▓▓▓|   ', ' └───┘   / \\    '],
            [' ┌───┐░         ', ' │░░░│\\ (ˆ‿ˆ)   ', ' │░░░│ /|▓▓▓|   ', ' └───┘   / \\    '],
            [' ┌───┐░  nom    ', ' │░◎░│\\ (ˆ○ˆ)ノ◎', ' │░░░│ /|▓▓▓|   ', ' └───┘   / \\    '],
            [' ┌───┐   nom!   ', ' │   │  (ˆ~ˆ)ノ◎', ' │  ▪│ /|▓▓▓|   ', ' └───┘   / \\    '],
        ],
        "masks": [
            [' mmmmm          ', ' m   m  .....   ', ' m  mm .......  ', ' mmmmm   ...    '],
            [' mmmmmy         ', ' myyymm .....   ', ' myyym .......  ', ' mmmmm   ...    '],
            [' mmmmmy  yyy    ', ' myyymm ....... ', ' myyym .......  ', ' mmmmm   ...    '],
            [' mmmmm          ', ' m   m  ....... ', ' m  mm .......  ', ' mmmmm   ...    '],
        ],
    },
    "hype": {
        "desc": 'up on his feet, dancing',
        "frames": [
            ['  ♪          ♫  ', '  \\(ˆ▽ˆ)/       ', '    |▓▓▓|       ', '    /   >       '],
            ['     ♫    ♪     ', '  /(ˆ▽ˆ)\\       ', '    |▓▓▓|       ', '    <   \\       '],
            ['  ♪   ♫         ', '  \\(ˆoˆ)/       ', '    |▓▓▓|       ', '    /   \\       '],
            ['        ♫   ♪   ', '   (ˆ▽ˆ)/  YEAH ', '   /|▓▓▓|       ', '    <   >       '],
        ],
        "masks": [
            ['  y          y  ', '  .......       ', '    .....       ', '    .....       '],
            ['     y    y     ', '  .......       ', '    .....       ', '    .....       '],
            ['  y   y         ', '  .......       ', '    .....       ', '    .....       '],
            ['        y   y   ', '   ......  yyyy ', '   ......       ', '    .....       '],
        ],
    },
    "dead": {
        "desc": 'flat on the floor, flies circling',
        "frames": [
            ['   °  ·         ', '                ', ' (x_x)▓▓▓══     ', '▔▔▔▔▔▔▔▔▔▔▔▔▔▔  '],
            ['    · °  ·      ', '                ', ' (x_x)▓▓▓══     ', '▔▔▔▔▔▔▔▔▔▔▔▔▔▔  '],
            ['  °  · °        ', '                ', ' (+_+)▓▓▓══     ', '▔▔▔▔▔▔▔▔▔▔▔▔▔▔  '],
            ['   · °  ·  RIP  ', '                ', ' (x_x)▓▓▓══     ', '▔▔▔▔▔▔▔▔▔▔▔▔▔▔  '],
        ],
        "masks": [
            ['   s  s         ', '                ', ' ...........    ', 'wwwwwwwwwwwwww  '],
            ['    s s  s      ', '                ', ' ...........    ', 'wwwwwwwwwwwwww  '],
            ['  s  s s        ', '                ', ' ...........    ', 'wwwwwwwwwwwwww  '],
            ['   s s  s  mmm  ', '                ', ' ...........    ', 'wwwwwwwwwwwwww  '],
        ],
    },
    "tableflip": {
        "desc": 'flipping the damn table',
        "frames": [
            ['         ┳━┳    ', '   (ಠ_ಠ)  ┃     ', '   /|▓▓▓|\\      ', '    /   \\       '],
            ['       ┳━┳      ', '  (╬ಠ益ಠ)       ', '   /|▓▓▓|\\      ', '    /   \\       '],
            ['          ┻━┻   ', '  (╯°□°)╯ ~     ', '    |▓▓▓|       ', '    /   \\       '],
            ['  FUCK      ┻   ', '  (╯°□°)╯    ━┻ ', '    |▓▓▓|       ', '    /   \\       '],
        ],
        "masks": [
            ['         www    ', '   .....  w     ', '   .......      ', '    .....       '],
            ['       www      ', '  .......       ', '   .......      ', '    .....       '],
            ['          www   ', '  ........s     ', '    .....       ', '    .....       '],
            ['  eeee      w   ', '  ........   ww ', '    .....       ', '    .....       '],
        ],
    },
}
