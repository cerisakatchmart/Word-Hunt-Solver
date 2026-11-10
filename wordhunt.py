#!/usr/bin/env python3
"""GamePigeon Word Hunt solver.

Finds every dictionary word that can be traced on the board by moving between
adjacent tiles (including diagonals) without reusing a tile, then ranks them
by Word Hunt's scoring.

Usage:
    python3 wordhunt.py oatrihpshtnrenei
    python3 wordhunt.py "oatr ihps htnr enei" --show 5
    python3 wordhunt.py            # prompts for the board
"""

import argparse
import math
import sys

DEFAULT_DICT = "/usr/share/dict/words"
MIN_LEN = 3


# ---------------------------------------------------------------- scoring

def score(word: str) -> int:
    """Word Hunt points: 3→100, 4→400, 5→800, then +400 per extra letter."""
    n = len(word)
    if n < 3:
        return 0
    if n == 3:
        return 100
    if n == 4:
        return 400
    if n == 5:
        return 800
    return 1400 + (n - 6) * 400


# ---------------------------------------------------------------- trie

class TrieNode:
    __slots__ = ("children", "word")

    def __init__(self):
        self.children = {}
        self.word = None  # full word stored at terminal nodes


def build_trie(words):
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            node = node.children.setdefault(ch, TrieNode())
        node.word = w
    return root


def load_words(path, max_len):
    """Lowercase alphabetic words of a playable length (skips proper nouns)."""
    words = set()
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if MIN_LEN <= len(w) <= max_len and w.isalpha() and w.islower():
                words.add(w)
    return words


# ---------------------------------------------------------------- board

def parse_board(text):
    letters = [c.lower() for c in text if c.isalpha()]
    size = math.isqrt(len(letters))
    if size < 2 or size * size != len(letters):
        raise ValueError(
            f"Board must be a square grid of letters (got {len(letters)})."
        )
    return [letters[r * size:(r + 1) * size] for r in range(size)]


def neighbors(size):
    """Precompute adjacency (8 directions) for each cell index."""
    adj = []
    for r in range(size):
        for c in range(size):
            cells = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        cells.append(nr * size + nc)
            adj.append(cells)
    return adj


# ---------------------------------------------------------------- solver

def solve(board, trie):
    """DFS from every tile, pruning with the trie.

    Returns {word: path} where path is a list of cell indices (first path found).
    """
    size = len(board)
    flat = [ch for row in board for ch in row]
    adj = neighbors(size)
    found = {}
    visited = [False] * len(flat)
    path = []

    def dfs(i, node):
        child = node.children.get(flat[i])
        if child is None:
            return  # no word starts with this prefix -> prune
        visited[i] = True
        path.append(i)
        if child.word and child.word not in found:
            found[child.word] = path.copy()
        for j in adj[i]:
            if not visited[j]:
                dfs(j, child)
        path.pop()
        visited[i] = False

    for i in range(len(flat)):
        dfs(i, trie)
    return found


# ---------------------------------------------------------------- output

def render_path(board, path):
    """Grid showing the order to swipe: step numbers on used tiles."""
    size = len(board)
    order = {cell: n + 1 for n, cell in enumerate(path)}
    lines = []
    for r in range(size):
        cells = []
        for c in range(size):
            i = r * size + c
            if i in order:
                cells.append(f"{board[r][c].upper()}{order[i]:<2}")
            else:
                cells.append(" · ")
        lines.append("  " + "  ".join(cells))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="GamePigeon Word Hunt solver")
    ap.add_argument("board", nargs="*", help="letters row by row, e.g. oatrihpshtnrenei")
    ap.add_argument("-d", "--dict", default=DEFAULT_DICT, help="word list file")
    ap.add_argument("-n", "--limit", type=int, default=0, help="only list top N words")
    ap.add_argument("-s", "--show", type=int, default=0,
                    help="draw swipe paths for the top N words")
    args = ap.parse_args()

    text = " ".join(args.board) or input("Enter board letters row by row: ")
    try:
        board = parse_board(text)
    except ValueError as e:
        sys.exit(str(e))

    max_len = len(board) ** 2
    trie = build_trie(load_words(args.dict, max_len))
    found = solve(board, trie)

    ranked = sorted(found, key=lambda w: (-score(w), w))
    if args.limit:
        ranked = ranked[: args.limit]

    print("\n".join("  " + " ".join(ch.upper() for ch in row) for row in board))
    total = sum(score(w) for w in found)
    print(f"\n{len(found)} words, {total:,} possible points\n")

    for w in ranked:
        print(f"{score(w):>6}  {w.upper()}")

    for w in ranked[: args.show]:
        print(f"\n{w.upper()} ({score(w)})")
        print(render_path(board, found[w]))


if __name__ == "__main__":
    main()
