# Word-Hunt-Solver
I love playing WordHunt!

## Usage

**Web interface** — type the board into a 4x4 grid, then click any word to see how to swipe it:

```bash
python3 server.py
```

Then open http://localhost:8000.

**Command line:**

```bash
python3 wordhunt.py oatrihpshtnrenei --limit 20 --show 3
```

Both accept `--dict FILE` to use a different word list (default: `/usr/share/dict/words`).
