# Wireframes

Structural prototypes for each character's stance and movement — self-contained HTML, open
any file directly in a browser. Same spirit as [`../concept-art/`](../concept-art/README.md):
a design reference, not a game asset.

| File | Character |
|---|---|
| `paladin.html` | grounded, square, almost-locked-knee stance; slow heavy breathing sway with a periodic shield-arm "readiness" flex |
| `gunslinger.html` | contrapposto, weight on the back foot, gun hand coiled near the holster; body nearly still except a fast tremor in the gun hand and a slow coat-tail sway |
| `alchemist.html` | hunched forward, bent knees, oversized head; constant small motion — vial hand rotating, head tilting, satchel bouncing |

Each page renders an animated SVG stick figure — an 18-bone humanoid skeleton (spine chain,
both arms, both legs, plus stub bones for a back-mounted item and a belt) built from a small
per-character data block (`RIG` in the page's own `<script>`) that a shared, hand-rolled 2D
forward-kinematics solver walks every frame. Three things are defined per character:

- **Stance** — each bone's rest-pose rotation. This *is* the posture: how wide the feet are
  planted, how bent the knees are, where the hands sit. Click "Pause (view stance)" on any
  page to freeze the animation and inspect it exactly.
- **Movement** — a sine-wave oscillation layered on top of the stance per bone (amplitude,
  frequency, phase), so each character idles with a gait that's actually theirs rather than
  a shared default loop. Movement is meant to read as an extension of the character's
  established identity (see each page's "Movement" note and the linked `design/*.md`), not
  as a separate animation decision.
- **Component map** — nine labeled attachment points (head, chest, back, belt, both
  shoulders, both hands, feet), each following the bone chain during animation and each
  annotated with what art belongs there and what it should look like. This is the "grand
  vision" layer: a written target for whoever illustrates or rigs the real part next.

## Art attachment

Every one of the 9 slots on all 3 characters (27 total) now carries a working `art` block —
this isn't a labeled point plus a proof of concept anymore, it's the full demo. A slot's `art`
is either a real image or a procedurally drawn icon:

```js
// real image — the Paladin's head, a crop of art_reference/paladin/portrait.png
art: { src:'assets/paladin_head.png', bone:'head_stub', t:1.0, w:70, h:70,
       anchor:{x:0.5,y:0.5}, rotationOffset:90 }

// procedural icon — every other slot on all three characters, since no other part art
// exists yet: a small vector shape list in the character's palette, generated the same
// way concept-art/cards/*.html generates its card icons — correct and distinct, not a
// substitute for real art
art: { bone:'chest', t:0.5, w:80, h:66, anchor:{x:0.5,y:0.5}, rotationOffset:90, shapes:[
  {tag:'rect', attrs:{x:9,y:6,width:62,height:52,rx:9, fill:'base', stroke:'#0c1120', 'stroke-width':2}},
  {tag:'circle', attrs:{cx:40,cy:28,r:9, fill:'accent', stroke:'color','stroke-width':2}},
  // ...
]}
```

`shapes` entries are plain SVG element descriptors (`tag` + `attrs`); `fill`/`stroke` values of
`'color'`, `'accent'`, or `'base'` resolve against that character's palette (declared once at
the top of the RIG object) so every generated part stays visually consistent with the real art
next to it. Whichever kind a slot uses, it's positioned at the named bone's world position for
the given `t`, then rotated to track that bone's current angle — `rotationOffset` cancels out
the bone's own rest-pose rotation so the art sits upright by default and only rotates by however
much the rig moves from there. Every one of the 27 `rotationOffset` values was checked with a
small script that re-derives each bone's rest-world-angle from the actual `RIG` data and
confirms the resulting art rotation is exactly 0° at stance — not eyeballed.

The framed border on every part is intentional: this is a calibration tool, so it stays honest
about being an unmasked placeholder rather than a finished cutout. Two toggles control what's
visible: **"Hide art overlay"** removes all part art to see the bare skeleton (useful for rig
work); **"Hide attachment markers"** removes the diamond calibration points to see the art
alone (useful for judging the read). Both default on, layered together, so misalignment is easy
to spot while iterating.

Wiring up real art once it exists is mechanical either way: drop an image in `assets/` and swap
`shapes` for `src` on that slot — same `bone`/`t`/`w`/`h`/`anchor`/`rotationOffset` fields,
tuned against the live preview until it tracks correctly.

## Movement: Idle, Attack, Self buff

Beyond the continuous idle gait, each character now has two triggered, one-shot moves —
**Attack** and **Self buff** — playable from buttons above the rig, so you can actually watch
how each character's stance and material read carry into their other animations, not just
standing still. A move is a short list of keyframe poses (bone → angle delta from stance) at
fractional times through its duration, interpolated with smoothstep easing:

```js
attack: {
  duration: 0.9,
  keyframes: [
    { at:0.0,  pose:{} },
    { at:0.25, pose:{ r_upper_arm:-35, r_forearm:-25, chest:-6, spine:-4, l_forearm:10 } },
    { at:0.5,  pose:{ r_upper_arm:55,  r_forearm:15,  chest:10, spine:6,  l_forearm:-5 } },
    { at:1.0,  pose:{} },
  ],
  effect: { bone:'r_hand', t:1, type:'flash', peakAt:0.5, width:0.12, color:'#f3d68a' },
}
```

Only the bones a move actually poses stop taking their idle sine sway while it plays — the legs
keep breathing through the Paladin's mace swing, for instance — and every move auto-returns to
idle when it finishes (or immediately, via the **Idle / gait** button, which also cancels a move
early). An optional `effect` drives a small glow/flash ring at a bone, for a bit of combat
feedback (a muzzle flash, a sigil pulse) without drawing a full particle system.

The three characters' Attack/Buff read distinctly on purpose, extending the same traits their
stance and idle gait already establish — see each page's "Movement" section for the specifics
(mace swing vs. a half-second gunshot vs. a loose, off-balance flask toss; a presented shield vs.
a showman's cylinder spin vs. a held-up, fizzing vial).

**What this does and doesn't fix.** All of this answers "can art be mapped onto the wireframe and
previewed through multiple movements" — yes, for all 27 slots and all three motion states now.
It does **not** touch the re-integration gap described above: the bone names, coordinate scheme,
and this attachment/move format are still local to this HTML/SVG tool, not Spine's slot/
attachment model, `edits.json`'s schema, or its animation format. Everything validated here still
has to be manually re-authored inside the real pipeline once someone has access to it.

## Why HTML and not a Godot scene or a Spine skeleton

This mod's actual combat rigs are Spine skeletons, and [`../spine/README.md`](../spine/README.md)
is explicit that `spine/<character>/` is **generated, do-not-hand-edit** build output — the
only source of truth for stance, posture, proportions, and hidden parts is
`skeletons/<character>/edits.json` inside the external
[`sts2-reskin-pipeline`](https://github.com/r0zar/sts2-reskin-pipeline) workbench, which isn't
checked into this repo. There's also no in-repo Godot scene using `Skeleton2D`/`Bone2D` today —
the game's own animation is loaded programmatically at runtime (see
`HelloSpireCode/Characters/CharacterSkeletons.cs`).

So a wireframe that's both hand-editable *in this repo* and immediately viewable without the
base game, the Spine editor, or the external workbench has to be its own thing. HTML+SVG was
the natural fit — it's the format `concept-art/` already uses for exactly this kind of
pre-production reference, it needs no build step or network access (no webfonts, unlike
`concept-art/*.html` — this is meant to be poked at and iterated on, not just read), and the
"component map" slots are just labeled points on a bone chain, which is a small step from
being literal attachment points once a rig is authored for real.

## Where this goes next

Nothing here writes to `spine/` or touches the mod's runtime rendering — it's a planning
layer that sits upstream of the workbench. The intended handoff, once real character art
exists: the stance numbers and slot list here become the starting values for that
character's `edits.json`, and the slot vision notes become the brief for `art_in/<character>/`.
Until then, these pages are the place to iterate on proportions, posture, and gait before
spending Spine-editor time on any of it.
