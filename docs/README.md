# docs

| page | content |
|---|---|
| `abconv-frame-flip.html` | what was wrong with the crossing frame in abconv (finding F2) and what eic/afterburner PR #38 and PR #42 change, with drawings |

The page loads `style.css`, `charts.js`, `figure-data.js` and KaTeX from cdn.jsdelivr.net. To view it, serve the
folder, for example:

```bash
python3 -m http.server 8765 --directory docs
```

Every number on the page comes from `figure-data.js`. To regenerate it from the 2026-11-07 beam-validation outputs:

```bash
uv run --no-project --with numpy python docs/make_figure_data.py /data/dis-autoresearch/beam-validation
```
