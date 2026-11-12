# Word-Hunt-Solver
This project was mainly for me to just play around with Claude Code and learn more about coding with agents.

## Usage

**Web interface:** live at https://cerisakatchmart.github.io/Word-Hunt-Solver/. `static/` is a self-contained page. The solver runs in the browser and loads its dictionary from `static/words.txt`, so any static host works. Pushing changes under `static/` to `main` redeploys the GitHub Pages site. You type the board into a 4x4 grid, then click any word to see how to swipe it. To try it locally:

```bash
python3 -m http.server 8000 -d static
```

Then open http://localhost:8000.

**Command line:**

```bash
python3 wordhunt.py oatrihpshtnrenei --limit 20 --show 3
```

The command line accepts `--dict FILE` to use a different word list (default: `/usr/share/dict/words`). `static/words.txt` was generated from that same list, keeping lowercase words of 3–16 letters.
