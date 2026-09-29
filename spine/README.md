# spine/ — generated, do not hand-edit

Everything under `spine/<character>/` is a **build output** of the character workbench,
[sts2-reskin-pipeline](https://github.com/r0zar/sts2-reskin-pipeline). So are the three
`HelloSpire/shaders/<character>_repaint.gdshader` files. Each `spine/<character>/SOURCE.json`
records the workbench commit, donor rig and content hashes that produced the folder.

The workbench is the **only** source of truth for what a character looks like:

| What | Where it is defined |
|---|---|
| donor rig (movement set) | `config/paths.toml` |
| colours — combat pages *and* the rest-site/shop shader | `config/palettes.toml` |
| stance, posture, proportions, hidden parts | `skeletons/<character>/edits.json` |
| replacement part art | `art_in/<character>/` |

To change a character: edit those files (or use the previewer), then

```
uv run tools/package.py <character> --install-hellospire
```

which rebuilds the rig, regenerates the shader, and writes both here and into your game's
`mods/HelloSpire/`. Commit the result **together with** the workbench change that produced it.
`uv run tools/package.py all --check` tells you whether this repo has drifted from the workbench.

Why so strict: the game only rejects a co-op partner whose *model database* differs. Two
players with the same mod version but different rig pages would both load fine and see two
different characters. Consistency across every client depends on every rig file in this folder
coming from one place, at one commit.
